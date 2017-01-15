import datetime
import json
import logging
import mimetypes
import os
import re
import tempfile

from celery import shared_task

from PIL import Image
from django.core.files import File
from django.core.files.uploadedfile import TemporaryUploadedFile, SimpleUploadedFile
from django.utils import timezone

from storage import helpers
from storage.helpers import resolve_dict, get_first_filled_value
from storage.tools import ffmpeg
from storage.tools.exiftool import get_exiftool_info, extract_any_embed_image

logger = logging.getLogger(__name__)


@shared_task
def process_media_state(media_id):
    from storage.models import Media
    try:
        media = Media.objects.get(pk=media_id)
    except Media.DoesNotExist:
        return

    media.processing_state.run(media)


# TODO: Have separate task for every processing -- to have reasonable tasks names, not single entry point


class MediaState:
    STATE_CODE = None

    STATES = {}

    @classmethod
    def get_state(cls, code):
        return cls.STATES.get(code, UnknownMediaState)

    @classmethod
    def post_save(cls, media):
        pass

    @classmethod
    def run(cls, media):
        try:
            cls.process(media)
        except Exception as ex:
            # That is breaking an abstraction
            media.processing_state_code = - cls.STATE_CODE
            media.save()
            raise

        media.processing_state = cls.get_next_state(media)

        # That would trigger execution of the next state
        media.save()
        cls.post_save(media)

    @classmethod
    def get_next_state(cls, media):
        raise NotImplementedError()

    @classmethod
    def process(cls, media):
        raise NotImplementedError()


class InitialMediaState(MediaState):
    STATE_CODE = 0

    @classmethod
    def get_next_state(cls, media):
        return MetadataMediaState

    @classmethod
    def process(cls, media):
        logger.debug("do nothing")


class MetadataMediaState(MediaState):
    STATE_CODE = 1

    @classmethod
    def get_next_state(cls, media):
        if media.media_type == media.MEDIA_VIDEO:
            return ScreenshotMediaState
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """check size, hash, get proper content-type, other metadata (e.g. duration)"""
        logger.debug("extract metadata")


class ScreenshotMediaState(MediaState):
    STATE_CODE = 2

    VIDEO_SCREENSHOT_SECOND = 10
    SCREENSHOT_SETTINGS = {
        'format': 'JPEG',
        'quality': 95,
        'progressive': True,
        'optimize': True,
    }

    @classmethod
    def get_next_state(cls, media):
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """Extract screenshot of the video"""
        if media.media_type != media.MEDIA_VIDEO:
            return

        logger.debug("extract screenshot")

        screenshot_second = min(media.duration.total_seconds() // 3, cls.VIDEO_SCREENSHOT_SECOND)

        screenshot = TemporaryUploadedFile(name='screenshot.jpg', content_type='', size=0, charset='')

        with tempfile.TemporaryFile('w+b') as screenshot_raw:
            ffmpeg.get_screenshot(media.content.path, seconds_offset=screenshot_second, hide_log=True,
                                  target=screenshot_raw)

            with Image.open(screenshot_raw) as image:
                image.save(screenshot, **cls.SCREENSHOT_SETTINGS)

        # Don't use screenshot directly since it would be deleted before closing, making TempFile crash
        media.screenshot = File(screenshot)


class ThumbnailMediaState(MediaState):
    STATE_CODE = 3

    THUMBNAIL_RESIZE_SETTINGS = {
        'size': (160, 160),
        'resample': Image.LANCZOS,  # Image.NEAREST | Image.BILINEAR | Image.BICUBIC | Image.LANCZOS
    }

    THUMBNAIL_SETTINGS = {
        'format': 'JPEG',
        'quality': 95,
        'progressive': True,
        'optimize': True,
    }

    @classmethod
    def get_next_state(cls, media):
        return ClassifyMediaState

    @classmethod
    def post_save(cls, media):
        from channels import Group

        Group(f'upload-{media.uploader_id}').send({
            'text': json.dumps(['thumbnail', {
                'media': {
                    'id': media.id,
                    'thumbnail': media.thumbnail.url if media.thumbnail else None,
                }
            }
        ])})

    @classmethod
    def process(cls, media):
        """Extract thumbnail from image or video's screenshot"""
        logger.debug("extract thumbnail")

        if media.media_type == media.MEDIA_IMAGE:
            source = media.content
        elif media.media_type == media.MEDIA_VIDEO:
            source = media.screenshot
        else:
            # Nothing to do
            return

        thumbnail_file = SimpleUploadedFile(name='thumbnail.jpg', content=b'', content_type='image/jpeg')

        try:
            with open(source.path, 'rb') as f:
                media.thumbnail = cls.generate_thumbnail_from_fp(f=f, target=thumbnail_file,
                                                                 needed_rotate_degree=media.needed_rotate_degree)
        except OSError as ex:
            # Fallback to embed thumbnail
            logger.warning(f'Failed to generate thumbnail from {media.mimetype!r} file => try embed resource')
            with tempfile.TemporaryFile('w+b') as embed_image:
                # Use biggest image to generate thumbnail
                extract_any_embed_image(media.metadata, source.path, target=embed_image, biggest=True)

                media.thumbnail = cls.generate_thumbnail_from_fp(f=embed_image, target=thumbnail_file,
                                                                 needed_rotate_degree=media.needed_rotate_degree)

    @classmethod
    def generate_thumbnail_from_fp(cls, f, target, needed_rotate_degree):
        with Image.open(f) as image:
            image.thumbnail(**cls.THUMBNAIL_RESIZE_SETTINGS)
            # TODO: Sharpen by taste or multi-step downsampling

            # Rotate thumbnail, not whole image
            if needed_rotate_degree:
                # PIL rotate rotates counter clockwise => invert it
                thumbnail = image.rotate(-needed_rotate_degree, expand=True)
            else:
                thumbnail = image

            thumbnail.save(target, **cls.THUMBNAIL_SETTINGS)
        return target


class ClassifyMediaState(MediaState):
    STATE_CODE = 4

    @classmethod
    def get_next_state(cls, media):
        return OptimizeForWebMediaState

    @classmethod
    def process(cls, media):
        """Classify the media"""
        from classification import group_media_into_shot, media_categories

        media.categories = list(media_categories.get(media=media))

        group_media_into_shot.process(media_id=media.pk, session_id=media.session_id)

        # TODO: Add more classification

        # TODO: Group SDR + HDR
        # TODO: Group bursts
        # TODO: Mark media with tags, e.g. "RAW", "Orig", "HDR", "Modified"


class OptimizeForWebMediaState(MediaState):
    STATE_CODE = 5

    @classmethod
    def get_next_state(cls, media):
        return ReadyMediaState

    @classmethod
    def process(cls, media):
        """Optimize media for web, e.g. transcode video (multiple codecs) and pack images, find good screenshot"""
        # See http://superuser.com/questions/538112/meaningful-thumbnails-for-a-video-using-ffmpeg
        logger.debug("optimize")
        # TODO: Implement generating content, optimized for viewing in browser, e.g. max 2880 x 1800, jpeg / mp4
        # TODO: Consider generating "original rotated" media, identical with quality but ready for usage


class ReadyMediaState(MediaState):
    STATE_CODE = 6

    @classmethod
    def run(cls, media):
        # do nothing
        pass


class UnknownMediaState(MediaState):
    STATE_CODE = None

    @classmethod
    def run(cls, media):
        # nothing to do
        pass


if not MediaState.STATES:
    MediaState.STATES = (InitialMediaState, MetadataMediaState, ScreenshotMediaState, ThumbnailMediaState,
                         ClassifyMediaState, OptimizeForWebMediaState, ReadyMediaState, UnknownMediaState)
    MediaState.STATES = {state.STATE_CODE: state for state in MediaState.STATES}
