from django.utils.translation import ugettext_lazy as _


class ShotConstMixin:
    MEDIA_PHOTO = 1
    MEDIA_VIDEO = 2
    # MEDIA_AUDIO = 3
    MEDIA_TYPES = (
        (MEDIA_PHOTO, _('Photo')),
        (MEDIA_VIDEO, _('Video')),
        # (MEDIA_AUDIO, _('Audio')),
    )

    ORIENTATION_LANDSCAPE = 1
    ORIENTATION_PORTRAIT = 2
    ORIENTATION_SQUARE = 3
    ORIENTATIONS = (
        (ORIENTATION_LANDSCAPE, _('Landscape')),
        (ORIENTATION_PORTRAIT, _('Portrait')),
        (ORIENTATION_SQUARE, _('Square')),
    )

    ASPECT_OTHER = 0
    ASPECT_16_9 = 1
    ASPECT_4_3 = 2
    ASPECT_SQUARE = 3
    ASPECT_RATIOS = (
        (ASPECT_16_9, _('16:9')),
        (ASPECT_4_3, _('4:3')),
        (ASPECT_SQUARE, _('1:1')),
        (ASPECT_OTHER, _('Other')),
    )


class MediaConstMixin:
    """
    Workflow:
    1) RAW (source as-is)
    2) original JPEG / MOV (base compression + )
    3) processed JPEG
    """
    WORKFLOW_RAW = 1
    WORKFLOW_ORIGINAL = 2
    WORKFLOW_PROCESSED = 3
    WORKFLOW_TYPES = (
        (WORKFLOW_RAW, _('Raw')),
        (WORKFLOW_ORIGINAL, _('Original')),
        (WORKFLOW_PROCESSED, _('Processed')),
    )
