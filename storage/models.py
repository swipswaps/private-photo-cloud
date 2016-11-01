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
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE)
    media_type = None

    # actual values
    width = models.IntegerField(help_text=_('Width for use'))
    height = models.IntegerField(help_text=_('Height for use'))
    duration_seconds = models.DurationField()

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

    class Meta:
        abstract = True


class Photo(Media):
    media_type = ShotConstMixin.MEDIA_PHOTO

    # actual values
    duration_seconds = None


class Video(Media):
    media_type = ShotConstMixin.MEDIA_VIDEO
