import base64
import binascii
import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from .const import ShotConstMixin, MediaConstMixin
from .states import MediaState, InitialMediaState


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
    shot_at = models.DateTimeField()
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

    def generate_content_filename(instance, filename):
        if instance.show_at and instance.content_extension:
            return 'content/{0.uploader_id}/{0.show_at:%Y%m}/{0.sha1_hex}_{0.size_bytes}{0.content_extension}'.format(instance)
        return 'content/{0.uploader_id}/{0.sha1_hex}_{0.size_bytes}'.format(instance)

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
    # shot = models.ForeignKey(Shot, on_delete=models.CASCADE, null=True)
    media_type = models.IntegerField(choices=MEDIA_TYPES, null=True)

    shot_at = models.DateTimeField(null=True)
    # date to me used to show in catalog and to store files; it is a fallback if failed to extract real shot_at date
    show_at = models.DateTimeField(null=True)

    # actual values
    width = models.IntegerField(null=True, blank=True, help_text=_('Width for use'))
    height = models.IntegerField(null=True, blank=True, help_text=_('Height for use'))
    duration = models.DurationField(null=True, blank=True)

    content = models.FileField(upload_to=generate_content_filename)
    size_bytes = models.BigIntegerField()

    # content_width = models.IntegerField(null=True, blank=True, help_text=_('Content width, before rotation'))
    # content_height = models.IntegerField(null=True, blank=True, help_text=_('Content height, before rotation'))

    needed_rotate_degree = models.IntegerField(
        null=True, blank=True,  # null means we did not extract if from the media, ask user for correct orientation
        help_text=_('How much content data need to be rotated to get correct orientation'),
    )

    # is_default = models.BooleanField(default=False)

    processing_state_code = models.IntegerField(default=InitialMediaState.STATE_CODE)

    mimetype = models.CharField(max_length=127)
    # workflow_type = models.IntegerField(null=True, blank=True, choices=MediaConstMixin.WORKFLOW_TYPES)

    source_filename = models.CharField(max_length=255, blank=True)
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

    metadata = JSONField(default=dict)

    class Meta:
        unique_together = (
            ('uploader', 'sha1_b85', 'size_bytes'),
        )

    # hashers properties, are often used
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
    # /hashers properties

    @property
    def processing_state(self):
        return MediaState.get_state(self.processing_state_code)

    @processing_state.setter
    def processing_state(self, value):
        assert issubclass(value, MediaState), f'{value!r} must be instance of MediaState'
        self.processing_state_code = value.STATE_CODE

    @classmethod
    def process(cls, sender, instance, **kwargs):
        media = instance

        media.processing_state.run(media)


# We must make it static after initialization, otherwise methods would not work in FileField
Media.generate_content_filename = staticmethod(Media.generate_content_filename)
Media.generate_thumbnail_filename = staticmethod(Media.generate_thumbnail_filename)
Media.generate_screenshot_filename = staticmethod(Media.generate_screenshot_filename)


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
