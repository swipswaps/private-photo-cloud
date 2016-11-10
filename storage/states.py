# TODO: Implement actual processing per step
import tempfile

from PIL import Image
from django.core.files.uploadedfile import TemporaryUploadedFile, SimpleUploadedFile

from storage import ffmpeg


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
        print("do nothing")


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
        print("extract metadata")

        print(dir(media.content))

        if media.media_type == media.MEDIA_PHOTO:
            media.needed_rotate_degree = media.get_image_needed_rotate_degree(media.content.path)
        elif media.media_type == media.MEDIA_VIDEO:
            # videos are auto-rotated by ffmpeg during playout / screenshot extraction, so no rotation needed
            clean_metadata = dict(media.get_video_clean_metadata(media.content.path))

            media.needed_rotate_degree = 0
            media.duration = clean_metadata['duration']
        # otherwise keep need_rotation_degree = None


class ScreenshotMediaState(MediaState):
    STATE_CODE = 2

    @classmethod
    def get_next_state(cls, media):
        return ThumbnailMediaState

    @classmethod
    def process(cls, media):
        """Extract screenshot of the video"""
        if media.media_type != media.MEDIA_VIDEO:
            return

        print("extract screenshot")

        if media.duration and media.duration.total_seconds() < media.VIDEO_SCREENSHOT_SECOND * 2:
            screenshot_second = media.duration.total_seconds() // 3
        else:
            screenshot_second = media.VIDEO_SCREENSHOT_SECOND

        screenshot = TemporaryUploadedFile('screenshot.jpg', '', 0, '')

        with tempfile.TemporaryFile('w+b') as screenshot_raw:
            ffmpeg.get_screenshot(media.content.path, seconds_offset=screenshot_second, hide_log=True, target=screenshot_raw)

            with Image.open(screenshot_raw) as image:
                image.save(screenshot, 'JPEG', quality=media.JPEG_QUALITY)

        media.screenshot = screenshot


class ThumbnailMediaState(MediaState):
    STATE_CODE = 3

    @classmethod
    def get_next_state(cls, media):
        return OptimizeForWebMediaState

    @classmethod
    def process(cls, media):
        """Extract thumbnail from image or video's screenshot"""
        print("extract thumbnail")

        if media.media_type == media.MEDIA_PHOTO:
            source = media.content
        elif media.media_type == media.MEDIA_VIDEO:
            source = media.screenshot
        else:
            # Nothing to do
            return

        thumbnail_file = SimpleUploadedFile('thumbnail.jpg', b'', 'image/jpeg')

        with open(source.path, 'rb') as f:
            with Image.open(f) as image:
                image.thumbnail(media.THUMBNAIL_BOX, Image.LANCZOS)

                # Rotate thumbnail, not whole image
                if media.needed_rotate_degree:
                    # PIL rotate rotates counter clockwise => invert it
                    thumbnail = image.rotate(-media.needed_rotate_degree, expand=True)
                else:
                    thumbnail = image

                thumbnail.save(thumbnail_file, 'JPEG', quality=media.JPEG_QUALITY)

        media.thumbnail = thumbnail_file



class OptimizeForWebMediaState(MediaState):
    STATE_CODE = 4

    @classmethod
    def get_next_state(cls, media):
        return ReadyMediaState

    @classmethod
    def process(cls, media):
        """Optimize media for web, e.g. transcode video (multiple codecs) and pack images"""
        print("optimize")


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
