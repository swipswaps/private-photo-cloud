import base64
import binascii
import datetime
import re

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from .const import ShotConstMixin, MediaConstMixin

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
    RE_ORIENTAION = re.compile('^Rotate (?P<degree>\d+)(?P<counter> CW)?$')

    THUMBNAIL_BOX = (128, 128)

    def generate_content_filename(instance, filename):
        # TODO: Add extension
        return f'{instance.uploader_id}_{instance.sha1_hex}_{instance.size_bytes}'

    def generate_thumbnail_filename(instance, filename):
        return f'thumbnail_{instance.id}.jpg'

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
    duration_seconds = models.DurationField(null=True, blank=True, )

    content = models.FileField(upload_to=generate_content_filename)
    size_bytes = models.BigIntegerField()

    content_width = models.IntegerField(null=True, blank=True, help_text=_('Content width'))
    content_height = models.IntegerField(null=True, blank=True, help_text=_('Content height'))

    needed_rotate_degree = models.IntegerField(
        null=True, blank=True,  # null means we did not extract if from the image, need to guess
        help_text=_('How much content data need to be rotated to get correct orientation'),
    )

    is_default = models.BooleanField(default=False)

    mimetype = models.CharField(max_length=127)
    workflow_type = models.IntegerField(null=True, blank=True, choices=MediaConstMixin.WORKFLOW_TYPES)

    source_filename = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=63, blank=True)
    source_lastmodified = models.DateTimeField(null=True)
    sha1_b85 = models.CharField(max_length=25, db_index=True)

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

        with Image.open(media.content) as image:
            media.needed_rotate_degree = cls.get_image_needed_rotate_degree(media.content)

            image.thumbnail(cls.THUMBNAIL_BOX, Image.LANCZOS)

            # Rotate thumbnail, not whole image
            if media.needed_rotate_degree:
                # PIL rotate rotates counter clockwise => invert it
                thumbnail = image.rotate(-media.needed_rotate_degree, expand=True)
            else:
                thumbnail = image

            thumbnail.save(thumbnail_file, 'JPEG', quality=90)

        media.thumbnail = thumbnail_file
        media.save()

    @classmethod
    def get_image_needed_rotate_degree(cls, file_field):
        """
        Extract orientation information from an image.

        We must use 3rd party tool here since there is a number of standards:
        - EXIF
        - XMP
        - IPTC
        - chunks (https://en.wikipedia.org/wiki/Portable_Network_Graphics#Ancillary_chunks)

        We use exiftool that is a standart in extracting metadata from images.
        """
        import pyexifinfo

        metadata = pyexifinfo.get_json(file_field.path)

        orientation = [(k, v)
                       for k, v in metadata[0].items()
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
        m = cls.RE_ORIENTAION.search(orientation[1])

        if not m:
            # Failed to parse
            raise NotImplementedError(f'Unsupported orientation: {orientation[1]}')

        degree = int(m.group('degree'), 10)

        if m.group('counter'):
            # counter-clockwise
            return degree

        # clock-wise
        return 360 - degree


# We must make it static after initialization, otherwise methods would not work in FileField
Media.generate_content_filename = staticmethod(Media.generate_content_filename)
Media.generate_thumbnail_filename = staticmethod(Media.generate_thumbnail_filename)


post_save.connect(Media.generate_photo_thumbnail, sender=Media)

"""
# TODO: Convert to model manager or proxy model

class Photo(Media):
    media_type = ShotConstMixin.MEDIA_PHOTO

    # actual values
    duration_seconds = None


class Video(Media):
    media_type = ShotConstMixin.MEDIA_VIDEO
"""
