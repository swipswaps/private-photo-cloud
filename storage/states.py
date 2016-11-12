import datetime
import logging
import re
import tempfile

from PIL import Image
from django.core.files.uploadedfile import TemporaryUploadedFile, SimpleUploadedFile

from storage.tools import ffmpeg
from storage.tools.exiftool import get_exiftool_info

logger = logging.getLogger(__name__)


class MediaState:
    STATE_CODE = None

    STATES = {}

    @classmethod
    def get_state(cls, code):
        return cls.STATES.get(code, UnknownMediaState)

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

    ORIENTATIONS_NO_DEGREE = {
        'Horizontal (normal)': 0,
    }
    RE_ORIENTATION = re.compile('^Rotate (?P<degree>\d+)(?P<counter> CW)?$')

    @classmethod
    def get_next_state(cls, media):
        if media.media_type == media.MEDIA_VIDEO:
            return ScreenshotMediaState
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """check size, hash, get proper content-type, other metadata (e.g. duration)"""
        import magic

        logger.debug("extract metadata")

        mimetype = magic.from_file(media.content.path, mime=True)

        if media.mimetype != mimetype:
            logger.warning(f'Content type {mimetype!r} is not recognized by browser (got {media.mimetype!r})')
            media.mimetype = mimetype

        # Set media_type
        media.media_type = cls.get_media_type_by_mimetype(media.mimetype)

        # TODO: Check file size (given with actual)
        # TODO: Check file hash (given with actual)

        if media.media_type == media.MEDIA_PHOTO:
            media.metadata = get_exiftool_info(media.content.path)

            media.needed_rotate_degree = cls.get_image_needed_rotate_degree(media.metadata)
        elif media.media_type == media.MEDIA_VIDEO:
            media.metadata = ffmpeg.get_ffprobe_info(media.content.path)
            video_stream = cls.get_video_stream(media.metadata)

            # videos are auto-rotated by ffmpeg during playout / screenshot extraction, so no rotation needed
            # OLD: video_stream['side_data_list'][0]['rotation'] OR video_stream['tags']['rotate']
            media.needed_rotate_degree = 0

            media.duration = datetime.timedelta(seconds=float(video_stream['duration']))
        else:
            # No rotation is needed, do not prompt the user
            media.needed_rotate_degree = 0

    @classmethod
    def get_media_type_by_mimetype(cls, mime_type):
        from storage.models import Media

        mime_type = mime_type.split('/')[0]

        if mime_type == 'image':
            return Media.MEDIA_PHOTO
        elif mime_type == 'video':
            return Media.MEDIA_VIDEO
        return Media.MEDIA_OTHER

    @classmethod
    def get_image_needed_rotate_degree(cls, metadata):
        """
        Extract orientation information from an image.

        We must use 3rd party tool here since there is a number of standards:
        - EXIF
        - XMP
        - IPTC
        - chunks (https://en.wikipedia.org/wiki/Portable_Network_Graphics#Ancillary_chunks)

        We use exiftool that is a standart in extracting metadata from images.
        """

        orientation = [(k, v)
                       for k, v in metadata.items()
                       if 'orientation' in k.lower()]

        if not orientation:
            # Was not found
            return None

        orientation_values = set(v for k, v in orientation)

        if len(orientation) > 1 and len(orientation_values) == 1:
            logger.warning(f'Multiple orientations found: {orientation}')
        elif len(orientation) > 1:
            raise NotImplementedError(f'Multiple orientations found: {orientation}')
        else:
            logger.info(f'Use orientation: {orientation[0]}')

        orientation = orientation[0]

        try:
            # First check exact match
            return cls.ORIENTATIONS_NO_DEGREE[orientation[1]]
        except KeyError:
            pass

        # Try to parse orientation
        m = cls.RE_ORIENTATION.search(orientation[1])

        if not m:
            # Failed to parse
            raise NotImplementedError(f'Unsupported orientation: {orientation[1]}')

        degree = int(m.group('degree'), 10)

        if m.group('counter'):
            # counter-clockwise
            return degree

        # clock-wise
        return 360 - degree

    @classmethod
    def get_video_stream(cls, metadata):
        video_streams = [stream for stream in metadata['streams'] if stream['codec_type'] == 'video']

        if len(video_streams) == 1:
            return video_streams[0]
        elif not video_streams:
            raise ValueError('Video file has no video streams')
        raise NotImplementedError(f'Videos with {len(video_streams)} video streams are not supported')


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
            ffmpeg.get_screenshot(media.content.path, seconds_offset=screenshot_second, hide_log=True, target=screenshot_raw)

            with Image.open(screenshot_raw) as image:
                image.save(screenshot, **cls.SCREENSHOT_SETTINGS)

        media.screenshot = screenshot


class ThumbnailMediaState(MediaState):
    STATE_CODE = 3

    THUMBNAIL_RESIZE_SETTINGS = {
        'size': (128, 128),
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
        return OptimizeForWebMediaState

    @classmethod
    def process(cls, media):
        """Extract thumbnail from image or video's screenshot"""
        logger.debug("extract thumbnail")

        if media.media_type == media.MEDIA_PHOTO:
            source = media.content
        elif media.media_type == media.MEDIA_VIDEO:
            source = media.screenshot
        else:
            # Nothing to do
            return

        thumbnail_file = SimpleUploadedFile(name='thumbnail.jpg', content=b'', content_type='image/jpeg')

        # TODO: If media is RAW image => extract thumbnail from file metadata

        try:
            with open(source.path, 'rb') as f:
                with Image.open(f) as image:
                    image.thumbnail(**cls.THUMBNAIL_RESIZE_SETTINGS)
                    # TODO: Sharpen by taste or multi-step downsampling

                    # Rotate thumbnail, not whole image
                    if media.needed_rotate_degree:
                        # PIL rotate rotates counter clockwise => invert it
                        thumbnail = image.rotate(-media.needed_rotate_degree, expand=True)
                    else:
                        thumbnail = image

                    thumbnail.save(thumbnail_file, **cls.THUMBNAIL_SETTINGS)

            media.thumbnail = thumbnail_file
        except OSError as ex:
            logger.exception(f'Failed to extract thumbnail for {media.mimetype!r}')


class OptimizeForWebMediaState(MediaState):
    STATE_CODE = 4

    @classmethod
    def get_next_state(cls, media):
        return ReadyMediaState

    @classmethod
    def process(cls, media):
        """Optimize media for web, e.g. transcode video (multiple codecs) and pack images, find good screenshot"""
        # See http://superuser.com/questions/538112/meaningful-thumbnails-for-a-video-using-ffmpeg
        logger.debug("optimize")


class ReadyMediaState(MediaState):
    STATE_CODE = 5

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
                         OptimizeForWebMediaState, ReadyMediaState, UnknownMediaState)
    MediaState.STATES = {state.STATE_CODE: state for state in MediaState.STATES}
