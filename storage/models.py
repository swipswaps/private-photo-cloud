import base64
import binascii
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


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

    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_('User that uploaded the media. He owns it.')
    )
    session_id = models.UUIDField()
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE, null=True)
    media_type = models.IntegerField(choices=MEDIA_TYPES)

    # actual values
    width = models.IntegerField(help_text=_('Width for use'))
    height = models.IntegerField(help_text=_('Height for use'))
    duration_seconds = models.DurationField(null=True)

    content = models.FileField()
    size_bytes = models.BigIntegerField()

    content_width = models.IntegerField(help_text=_('Content width'))
    content_height = models.IntegerField(help_text=_('Content height'))

    content_rotate_degree = models.IntegerField(
        default=0,
        help_text=_('How much content data must be rotated before use'),
    )

    is_default = models.BooleanField()

    mimetype = models.CharField(max_length=127)
    workflow_type = models.IntegerField(choices=MediaConstMixin.WORKFLOW_TYPES)

    source_filename = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=63, blank=True)
    source_lastmodified = models.DateTimeField(null=True)
    sha1_b85 = models.CharField(max_length=25, db_index=True)

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
        return self.sha1.encode('hex')

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


"""
# TODO: Convert to model manager or proxy model

class Photo(Media):
    media_type = ShotConstMixin.MEDIA_PHOTO

    # actual values
    duration_seconds = None


class Video(Media):
    media_type = ShotConstMixin.MEDIA_VIDEO
"""
