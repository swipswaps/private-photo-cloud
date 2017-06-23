import os

import logging
from django.conf import settings

# Do not use django.contrib.gis while it not easy to install
# from postgres_geometry.fields import PointField
from lib.point_field import PointField

from django.contrib.postgres.fields import JSONField, ArrayField, HStoreField
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from processing.states import ProcessingState
from storage.helpers import base85_to_hex, hex_to_base85
from storage.tools.sequence import get_next_value

from .const import ShotConstMixin, MediaConstMixin

logger = logging.getLogger(__name__)


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

    thumbnail = models.FileField(blank=True)
    thumbnail_width = models.IntegerField(null=True, blank=True)
    thumbnail_height = models.IntegerField(null=True, blank=True)


class Media(MediaConstMixin, models.Model):
    content_extension = None

    CONTENT_FILENAME_TMPL = 'content/{uploader_id}/{show_at:%Y%m/%d-%H%M%S}_{sha1_hex}{content_extension}'

    @staticmethod
    def generate_content_filename_permanent(uploader_id=None, show_at=None, sha1_hex=None, size_bytes=None, content_extension=None):
        return Media.CONTENT_FILENAME_TMPL.format(
            uploader_id=uploader_id,
            show_at=show_at,
            sha1_hex=sha1_hex,
            size_bytes=size_bytes,
            content_extension=content_extension
        )

    def generate_content_filename(instance, filename):
        # It is in initial file generation
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
    media_type = models.IntegerField(choices=MediaConstMixin.MEDIA_TYPES, null=True)

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

    categories = ArrayField(models.IntegerField(), blank=True, default=list)

    processing_state_code = models.IntegerField(default=ProcessingState.STATE_INITIAL)

    mimetype = models.CharField(max_length=127)
    # workflow_type = models.IntegerField(null=True, blank=True, choices=MediaConstMixin.WORKFLOW_TYPES)

    source_filename = models.CharField(max_length=255, blank=True)
    source_lastmodified = models.DateTimeField(null=True)
    sha1_b85 = models.CharField(max_length=25, db_index=True)

    screenshot = models.FileField(blank=True, upload_to=generate_screenshot_filename,
        help_text=_('Image taken from the video, sized 1:1 to rotated video')
    )

    thumbnail = models.FileField(blank=True, upload_to=generate_thumbnail_filename)
    thumbnail_width = models.IntegerField(null=True, blank=True)
    thumbnail_height = models.IntegerField(null=True, blank=True)

    metadata = JSONField(default=dict)

    shot_id = models.IntegerField(null=True, blank=True)
    camera = models.CharField(max_length=255, blank=True)

    gps_location = PointField(null=True, blank=True)
    gps_precision_m = models.FloatField(null=True, blank=True)
    gps_altitude_m = models.FloatField(null=True, blank=True)

    location = HStoreField(blank=True, default=dict)

    # TODO: Add field to store view-optimized content

    @classmethod
    def get_next_shot_id(cls):
        return get_next_value(cls.SHOT_SEQUENCE_NAME)

    class Meta:
        unique_together = (
            ('uploader', 'sha1_b85', 'size_bytes'),
        )

    @property
    def unique_key(self):
        return {
            'uploader_id': self.uploader_id,
            'sha1_b85': self.sha1_b85,
            'size_bytes': self.size_bytes,
        }

    # hashers properties, are often used
    @property
    def sha1_hex(self):
        return base85_to_hex(self.sha1_b85)

    @sha1_hex.setter
    def sha1_hex(self, digest_hex):
        self.sha1_b85 = hex_to_base85(digest_hex)

    # /hashers properties

    def process(self):
        ProcessingState.run(self.processing_state_code, self.id)

    @property
    def default_thumbnail_url(self):
        return settings.MEDIA_URL + self.generate_thumbnail_filename(self, None)

    @staticmethod
    def move_file(storage=None, old_name=None, new_name=None):
        assert new_name != old_name

        old_full_path = storage.path(old_name)
        new_full_path = storage.path(new_name)

        logger.info(f'Move file: {old_full_path} => {new_full_path}...')

        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        os.rename(old_full_path, new_full_path)

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        if created:
            instance.process()

    # TODO: Cache
    @classmethod
    def categories_w_count(cls, uploader=None):
        return [
            (c_id, c_name, Media.objects.filter(uploader=uploader, categories__contains=[c_id]).count())
            for c_id, c_name in cls.CATEGORIES
        ]

# We must make it static after initialization, otherwise methods would not work in FileField
Media.generate_thumbnail_filename = staticmethod(Media.generate_thumbnail_filename)
Media.generate_screenshot_filename = staticmethod(Media.generate_screenshot_filename)

post_save.connect(Media.post_save, sender=Media)

"""
Re-process not finished processes:

# TODO: Make management command out of it

from storage.models import *
for m_id in Media.objects.filter(processing_state_code__lt=6).values_list('id', flat=True):
    process_media_state.delay(m_id)
"""

"""
# TODO: Convert to model manager or proxy model

class Photo(Media):
    media_type = ShotConstMixin.MEDIA_IMAGE

    # actual values
    duration_seconds = None


class Video(Media):
    media_type = ShotConstMixin.MEDIA_VIDEO
"""
