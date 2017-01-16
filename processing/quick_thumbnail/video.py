import tempfile

from django.core.files import File
from django.core.files.uploadedfile import TemporaryUploadedFile, SimpleUploadedFile

from processing.media_processors import is_video


class ScreenShotByDurationVideoContent:
    VIDEO_SCREENSHOT_SECOND = 10
    SCREENSHOT_SETTINGS = {
        'format': 'JPEG',
        'quality': 95,
        'progressive': True,
        'optimize': True,
    }

    @staticmethod
    def run(media_type=None, duration=None, content=None):
        from storage.tools import ffmpeg
        from PIL import Image

        if not is_video(media_type):
            return

        screenshot_second = min(duration.total_seconds() // 3, ScreenShotByDurationVideoContent.VIDEO_SCREENSHOT_SECOND)

        # TODO: Refactor to generate only thumbnail

        screenshot = TemporaryUploadedFile(name='screenshot.jpg', content_type='', size=0, charset='')

        with tempfile.TemporaryFile('w+b') as screenshot_raw:
            ffmpeg.get_screenshot(content.path, seconds_offset=screenshot_second, hide_log=True,
                                  target=screenshot_raw)

            with Image.open(screenshot_raw) as image:
                image.save(screenshot, **ScreenShotByDurationVideoContent.SCREENSHOT_SETTINGS)

        # Don't use screenshot directly since it would be deleted before closing, making TempFile crash
        return 'screenshot', File(screenshot)


def ThumbnailByScreenShotDegree(media_type=None, screenshot=None, needed_rotate_degree=None):
    from processing.quick_thumbnail.thumbnail import Thumbnail

    if not is_video(media_type):
        return

    return 'thumbnail', Thumbnail.generate_from_file(screenshot, needed_rotate_degree=needed_rotate_degree)
