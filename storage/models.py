import base64
import binascii
import datetime
import re

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from .const import ShotConstMixin, MediaConstMixin
from .states import MediaState, InitialMediaState


# Create your models here.


class ShotCategory(models.Model):
    """
    - portrait (few big faces)
    - landscape (no faces or small ones)
    - selfie (shot with front camera)
    - slow-motion
    - panorama
    """
    pass


class Shot(ShotConstMixin, models.Model):
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_('User that uploaded the media. He owns it.')
    )

    media_type = models.IntegerField(choices=ShotConstMixin.MEDIA_TYPES)
    orientation = models.IntegerField(choices=ShotConstMixin.ORIENTATIONS)
    aspect_ratio = models.IntegerField(choices=ShotConstMixin.ASPECT_RATIOS)

    # common data from photos/videos
    shoot_at = models.DateTimeField()
    device = models.CharField(max_length=255, blank=True)
    width = models.IntegerField()
    height = models.IntegerField()
    duration_seconds = models.IntegerField(null=True, blank=True)

    thumbnail = models.ImageField(
        blank=True,
        width_field='thumbnail_width',
        height_field='thumbnail_height',
    )
    thumbnail_width = models.IntegerField(null=True, blank=True)
    thumbnail_height = models.IntegerField(null=True, blank=True)


class Media(MediaConstMixin, models.Model):
    MEDIA_PHOTO = 1
    MEDIA_VIDEO = 2
    MEDIA_OTHER = 3

    MEDIA_TYPES = (
        (MEDIA_PHOTO, _('Photo')),
        (MEDIA_VIDEO, _('Video')),
        (MEDIA_OTHER, _('Other')),
    )

    ORIENTATIONS_NO_DEGREE = {
        'Horizontal (normal)': 0,
    }
    RE_ORIENTATION = re.compile('^Rotate (?P<degree>\d+)(?P<counter> CW)?$')
    THUMBNAIL_BOX = (128, 128)
    JPEG_QUALITY = 95

    def generate_content_filename(instance, filename):
        # TODO: Add extension
        return f'content/{instance.uploader_id}/{instance.sha1_hex}_{instance.size_bytes}'

    def generate_thumbnail_filename(instance, filename):
        return f'thumbnail/{instance.uploader_id}/{instance.id}.jpg'

    def generate_screenshot_filename(instance, filename):
        return f'screenshot/{instance.uploader_id}/{instance.id}.jpg'

    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_('User that uploaded the media. He owns it.')
    )
    session_id = models.UUIDField()
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE, null=True)
    media_type = models.IntegerField(choices=MEDIA_TYPES)

    # actual values
    width = models.IntegerField(null=True, blank=True, help_text=_('Width for use'))
    height = models.IntegerField(null=True, blank=True, help_text=_('Height for use'))
    duration = models.DurationField(null=True, blank=True)

    content = models.FileField(upload_to=generate_content_filename)
    size_bytes = models.BigIntegerField()

    content_width = models.IntegerField(null=True, blank=True, help_text=_('Content width, before rotation'))
    content_height = models.IntegerField(null=True, blank=True, help_text=_('Content height, before rotation'))

    needed_rotate_degree = models.IntegerField(
        null=True, blank=True,  # null means we did not extract if from the image, need to guess
        help_text=_('How much content data need to be rotated to get correct orientation'),
    )

    is_default = models.BooleanField(default=False)

    processing_state_code = models.IntegerField(default=InitialMediaState.STATE_CODE)

    mimetype = models.CharField(max_length=127)
    workflow_type = models.IntegerField(null=True, blank=True, choices=MediaConstMixin.WORKFLOW_TYPES)

    source_filename = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=63, blank=True)
    source_lastmodified = models.DateTimeField(null=True)
    sha1_b85 = models.CharField(max_length=25, db_index=True)

    screenshot = models.ImageField(
        blank=True,
        width_field='width',
        height_field='height',
        upload_to=generate_screenshot_filename,
        help_text=_('Image taken from the video, sized 1:1 to rotated video')
    )

    thumbnail = models.ImageField(
        blank=True,
        width_field='thumbnail_width',
        height_field='thumbnail_height',
        upload_to=generate_thumbnail_filename
    )
    thumbnail_width = models.IntegerField(null=True, blank=True)
    thumbnail_height = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (
            ('uploader', 'sha1_b85'),
        )

    @property
    def processing_state(self):
        return MediaState.get_state(self.processing_state_code)

    @processing_state.setter
    def processing_state(self, value):
        assert issubclass(value, MediaState), f'{value!r} must be instance of MediaState'
        self.processing_state_code = value.STATE_CODE

    @property
    def sha1(self):
        return base64.b85decode(self.sha1_b85)

    @sha1.setter
    def sha1(self, digest):
        self.sha1_b85 = base64.b85encode(digest)

    @property
    def sha1_hex(self):
        return self.sha1.hex()

    @sha1_hex.setter
    def sha1_hex(self, digest_hex):
        self.sha1 = binascii.unhexlify(digest_hex)

    @property
    def media_type_by_text(self):
        if self.media_type == self.MEDIA_PHOTO:
            return 'image'
        elif self.media_type == self.MEDIA_VIDEO:
            return 'video'
        return 'application'

    @media_type_by_text.setter
    def media_type_by_text(self, mime_type):
        mime_type = mime_type.split('/')[0]
        if mime_type == 'image':
            self.media_type = self.MEDIA_PHOTO
        elif mime_type == 'video':
            self.media_type = self.MEDIA_VIDEO
        else:
            self.media_type = self.MEDIA_OTHER

    @property
    def source_lastmodified_time(self):
        return self.source_lastmodified.timestamp()

    @source_lastmodified_time.setter
    def source_lastmodified_time(self, number):
        self.source_lastmodified = datetime.datetime.fromtimestamp(
            number,
            datetime.timezone.utc)

    @classmethod
    def generate_photo_thumbnail(cls, sender, instance, **kwags):
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        media = instance

        if media.thumbnail or media.media_type != cls.MEDIA_PHOTO:
            return

        thumbnail_file = SimpleUploadedFile('thumbnail.jpg', b'', 'image/jpeg')

        with open(media.content.path, 'rb') as f:
            with Image.open(f) as image:
                media.needed_rotate_degree = cls.get_image_needed_rotate_degree(media.content.path)

                image.thumbnail(cls.THUMBNAIL_BOX, Image.LANCZOS)

                # Rotate thumbnail, not whole image
                if media.needed_rotate_degree:
                    # PIL rotate rotates counter clockwise => invert it
                    thumbnail = image.rotate(-media.needed_rotate_degree, expand=True)
                else:
                    thumbnail = image

                thumbnail.save(thumbnail_file, 'JPEG', quality=cls.JPEG_QUALITY)

        media.thumbnail = thumbnail_file
        media.save()

    VIDEO_SCREENSHOT_SECOND = 10

    @classmethod
    def generate_video_thumbnail(cls, sender, instance, **kwags):
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile, TemporaryUploadedFile
        from PIL import Image
        from storage.ffmpeg import get_screenshot

        media = instance

        if media.thumbnail or media.media_type != cls.MEDIA_VIDEO:
            return

        clean_metadata = dict(cls.get_video_clean_metadata(media.content.path))

        # videos are auto-rotated by ffmpeg during playout / screenshot extraction, so no rotation needed
        media.needed_rotate_degree = 0
        media.duration = clean_metadata['duration']

        if media.duration and media.duration.total_seconds() < cls.VIDEO_SCREENSHOT_SECOND * 2:
            screenshot_second = media.duration.total_seconds() // 3
        else:
            screenshot_second = cls.VIDEO_SCREENSHOT_SECOND

        thumbnail = SimpleUploadedFile('thumbnail.jpg', b'', 'image/jpeg')

        screenshot = TemporaryUploadedFile('screenshot.jpg', '', 0, '')

        with tempfile.TemporaryFile('w+b') as screenshot_raw:
            get_screenshot(media.content.path, seconds_offset=screenshot_second, hide_log=True, target=screenshot_raw)

            with Image.open(screenshot_raw) as image:

                image.save(screenshot, 'JPEG', quality=cls.JPEG_QUALITY)

                image.thumbnail(cls.THUMBNAIL_BOX, Image.LANCZOS)
                image.save(thumbnail, 'JPEG', quality=cls.JPEG_QUALITY)

        media.screenshot = screenshot
        media.thumbnail = thumbnail
        media.save()

    @classmethod
    def get_image_needed_rotate_degree(cls, filename):
        """
        Extract orientation information from an image.

        We must use 3rd party tool here since there is a number of standards:
        - EXIF
        - XMP
        - IPTC
        - chunks (https://en.wikipedia.org/wiki/Portable_Network_Graphics#Ancillary_chunks)

        We use exiftool that is a standart in extracting metadata from images.
        """
        from storage.exiftool import get_exiftool_info

        metadata = get_exiftool_info(filename)

        orientation = [(k, v)
                       for k, v in metadata.items()
                       if 'orientation' in k.lower()]

        if not orientation:
            # Was not found
            return None

        if len(orientation) > 1:
            raise NotImplementedError(f'Multiple orientations found: {orientation}')

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
    def get_video_clean_metadata(cls, filename):
        from storage.ffmpeg import get_ffprobe_info

        metadata = get_ffprobe_info(filename)

        streams = metadata['streams']

        video_streams = [stream for stream in streams if stream['codec_type'] == 'video']

        if not video_streams:
            return

        if len(video_streams) != 1:
            raise NotImplementedError(f'Videos with {len(video_streams)} video streams are not supported')

        video = video_streams[0]

        # yield 'rotate', video['side_data_list'][0]['rotation']
        # yield 'rotate', int(video['tags']['rotate'], 10)

        yield 'duration', datetime.timedelta(seconds=float(video['duration']))

    @classmethod
    def generate_metadata(cls, sender, instance, **kwargs):
        media = instance

        if media.size_bytes:
            return

        print(dir(media.content))


    @classmethod
    def process(cls, sender, instance, **kwargs):
        media = instance

        media.processing_state.run(media)


# We must make it static after initialization, otherwise methods would not work in FileField
Media.generate_content_filename = staticmethod(Media.generate_content_filename)
Media.generate_thumbnail_filename = staticmethod(Media.generate_thumbnail_filename)
Media.generate_screenshot_filename = staticmethod(Media.generate_screenshot_filename)


post_save.connect(Media.generate_photo_thumbnail, sender=Media)
post_save.connect(Media.generate_video_thumbnail, sender=Media)
post_save.connect(Media.generate_metadata, sender=Media)
post_save.connect(Media.process, sender=Media)


"""
# TODO: Convert to model manager or proxy model

class Photo(Media):
    media_type = ShotConstMixin.MEDIA_PHOTO

    # actual values
    duration_seconds = None


class Video(Media):
    media_type = ShotConstMixin.MEDIA_VIDEO
"""
