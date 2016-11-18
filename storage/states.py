import datetime
import json
import logging
import mimetypes
import os
import re
import tempfile

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile, SimpleUploadedFile
from django.utils import timezone

from storage import helpers
from storage.helpers import resolve_dict
from storage.tools import ffmpeg
from storage.tools.binhash import get_sha1_hex
from storage.tools.exiftool import get_exiftool_info, extract_embed_thubmail

logger = logging.getLogger(__name__)


class MediaState:
    STATE_CODE = None

    STATES = {}

    class InvalidUploadError(ValueError):
        pass

    @classmethod
    def get_state(cls, code):
        return cls.STATES.get(code, UnknownMediaState)

    @classmethod
    def run(cls, media):
        try:
            cls.process(media)
        except cls.InvalidUploadError as ex:
            logger.error(ex)
            media.delete()
            raise
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

    EXTENSION_BY_MIME = {
        'image/x-canon-cr2': '.cr2',
        'image/jpeg': '.jpg',
    }

    @classmethod
    def process(cls, media):
        """check size, hash, get proper content-type, other metadata (e.g. duration)"""
        import magic
        from storage.models import Media

        logger.debug("extract metadata")

        mimetype = magic.from_file(media.content.path, mime=True)

        user_file_extension = os.path.splitext(media.source_filename)[1].lower()

        if media.mimetype != mimetype:
            logger.info(f'Content type of {user_file_extension!r} is not recognized by'
                        f' browser (got {media.mimetype!r} instead of {mimetype!r})')
            media.mimetype = mimetype

        # Set media_type
        media.media_type = cls.get_media_type_by_mimetype(media.mimetype)

        media.content_extension = helpers.get_first_filled_value(cls.get_content_extension(media))

        if media.content_extension != user_file_extension:
            logging.info(f'Changed file extension: {user_file_extension!r} => {media.content_extension!r}')

        # Verify file size
        size_bytes = media.content.size

        if media.size_bytes != size_bytes:
            raise cls.InvalidUploadError(f'actual size does not match declared: {size_bytes!r} != {media.size_bytes!r}')

        # Verify file hash
        sha1_hex = get_sha1_hex(media.content.path)

        if media.sha1_hex != sha1_hex:
            raise cls.InvalidUploadError(f'actual SHA1 sum does not match declared: {sha1_hex!r} != {media.sha1_hex!r}')

        # It makes no sense to generate SHA1 for image content (i.e. without metadata) since metadata removal is usually
        # implies re-compression, so content changes.

        if media.media_type == media.MEDIA_PHOTO:
            # Alternative: exiv2 (faster but less formats) http://dev.exiv2.org/projects/exiv2/wiki/How_does_Exiv2_compare_to_Exiftool
            media.metadata = get_exiftool_info(media.content.path)

            media.needed_rotate_degree = cls.get_image_needed_rotate_degree(media.metadata)

            # TODO: Put flag and some fake value if failed to extract
            media.shoot_at = cls.get_image_shoot_date(media.metadata)

        elif media.media_type == media.MEDIA_VIDEO:
            media.metadata = ffmpeg.get_ffprobe_info(media.content.path)
            video_stream = cls.get_video_stream(media.metadata)

            # videos are auto-rotated by ffmpeg during playout / screenshot extraction, so no rotation needed
            # OLD: video_stream['side_data_list'][0]['rotation'] OR video_stream['tags']['rotate']
            media.needed_rotate_degree = 0

            media.duration = datetime.timedelta(seconds=float(video_stream['duration']))
            # TODO: Put flag and some fake value if failed to extract
            media.shoot_at = cls.get_video_shoot_date(media.metadata)

        else:
            # No rotation is needed, do not prompt user for it
            media.needed_rotate_degree = 0
            # TODO: Put flag and some fake value for shoot_at

        logger.info(f'Shoot at: {media.shoot_at!r}')

        content_suffix = Media.generate_content_filename(media, None)
        content_path = os.path.join(settings.MEDIA_ROOT, content_suffix)

        if content_path != media.content.path:
            logging.info(f'Move content file: {media.content.path} => {content_path}...')
            dirname = os.path.dirname(content_path)

            if not os.path.exists(dirname):
                os.mkdir(dirname)

            os.rename(media.content.path, content_path)
            media.content.name = content_suffix

    @classmethod
    def get_content_extension(cls, media):
        yield cls.EXTENSION_BY_MIME.get(media.mimetype)
        yield mimetypes.guess_extension(media.mimetype)

        user_file_extension = os.path.splitext(media.source_filename)[1].lower()
        logging.error(f'Unknown file extension for {media.mimetype!r} => fallback to user extension {user_file_extension}')
        yield user_file_extension

    @classmethod
    def get_image_shoot_date(cls, metadata):
        shoot_dates = [(k, v) for k, v in cls.get_image_shoot_date_options(metadata) if v]

        logger.debug(f'image shoot dates: {shoot_dates}')

        for k, v in shoot_dates:
            return cls.parse_shoot_at(v)

        raise NotImplementedError(f'Failed to extract image shoot date from:\n{json.dumps(dict(metadata), indent=4)}')

    IMAGE_SHOOT_KEYS = (
        # More precise should come first
        "Composite:SubSecCreateDate",
        "Composite:SubSecDateTimeOriginal",
        "Composite:SubSecModifyDate",
        "XMP:DateCreated",
        "EXIF:CreateDate",
        "EXIF:DateTimeOriginal",
        "EXIF:ModifyDate",
        "EXIF:GPSDateStamp",
    )

    @classmethod
    def get_image_shoot_date_options(cls, metadata):
        for k in cls.IMAGE_SHOOT_KEYS:
            yield k, metadata.get(k)

    @classmethod
    def get_video_shoot_date(cls, metadata):
        shoot_dates = [(k, v) for k, v in cls.get_video_shoot_date_options(metadata) if v]

        logger.debug(f'video shoot dates: {shoot_dates}')

        for k, v in shoot_dates:
            return cls.parse_shoot_at(v)

        raise NotImplementedError(f'Failed to extract video shoot date from:\n{json.dumps(dict(metadata), indent=4)}')

    SHOOT_DATE_FORMATS = (
        '%Y:%m:%d %H:%M:%S',        # 2016:10:19 21:08:00
        '%Y:%m:%d %H:%M:%S.%f',     # 2016:11:06 14:29:25.018
        '%Y-%m-%dT%H:%M:%S%z',      # 2016-10-22T14:39:13+0200
    )

    @classmethod
    def parse_shoot_at(cls, value):
        # Fix too short microseconds section (14:29:25.018 => 14:29:25.01800)
        value = re.sub(r'(?<=[.])(\d+)$', lambda m: m.group(1).ljust(6, '0'), value)

        for dt_format in cls.SHOOT_DATE_FORMATS:
            try:
                dt = datetime.datetime.strptime(value, dt_format)
            except ValueError:
                continue

            if not dt.tzinfo:
                """
                No timezone provided -- that means date is device date:

                a) for camera -- time of home region
                b) for smartphone:
                    1) without TZ adjustment -- time of home region
                    2) with TZ adjustment -- time of current region (see GPS coordinates)

                # TODO: Implement complex logic instead of converting to server TZ.
                """
                return timezone.get_current_timezone().localize(dt, is_dst=None)
            return dt

        raise NotImplementedError(value)

    VIDEO_SHOOT_KEYS = (
        'format:tags:com.apple.quicktime.creationdate',
        'format:tags:creation_time',
        'stream:{codec_type}:tags.creation_time',
    )

    @classmethod
    def get_video_shoot_date_options(cls, metadata):
        for k in cls.VIDEO_SHOOT_KEYS:
            if ':{codec_type}:' in k:
                for stream in metadata['streams']:
                    yield k.format(**stream), resolve_dict(k.replace(':{codec_type}:', ':'), {'stream': stream})
            else:
                yield k, resolve_dict(k, metadata)

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
            logger.info(f'Multiple orientations found: {orientation}')
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

        try:
            with open(source.path, 'rb') as f:
                media.thumbnail = cls.generate_thumbnail_from_fp(f=f, target=thumbnail_file,
                                                                 needed_rotate_degree=media.needed_rotate_degree)
        except OSError as ex:
            # Fallback to embed thumbnail
            logger.warning(f'Failed to generate thumbnail from {media.mimetype!r} file => try embed resource')
            with tempfile.TemporaryFile('w+b') as embed_image:
                extract_embed_thubmail(media.metadata, source.path, target=embed_image)
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
