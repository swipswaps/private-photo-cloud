from django.utils.translation import ugettext_lazy as _


class ShotConstMixin:
    MEDIA_IMAGE = 1
    MEDIA_VIDEO = 2
    # MEDIA_AUDIO = 3
    MEDIA_TYPES = (
        (MEDIA_IMAGE, _('Photo')),
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

    MEDIA_IMAGE = 1
    MEDIA_VIDEO = 2
    MEDIA_OTHER = 3

    MEDIA_TYPES = (
        (MEDIA_IMAGE, _('Image')),
        (MEDIA_VIDEO, _('Video')),
        (MEDIA_OTHER, _('Other')),
    )

    SHOT_SEQUENCE_NAME = 'media_shot'

    CATEGORY_IMAGE = 1
    CATEGORY_SELFIE = 2
    CATEGORY_PANORAMA = 3
    CATEGORY_SCREENSHOT = 4

    CATEGORY_VIDEO = 10
    CATEGORY_VIDEO_INTERVAL = 11
    CATEGORY_VIDEO_SLOMO = 12
    CATEGORY_VIDEO_WIDESCREEN = 13

    CATEGORY_BURST = 20

    CATEGORY_MEDIA_PORTRAIT = 21
    CATEGORY_MEDIA_LANDSCAPE = 22
    CATEGORY_MEDIA_SQUARE = 23

    CATEGORY_NON_MEDIA = 30

    CATEGORIES = (
        (CATEGORY_IMAGE, _("Image")),
        (CATEGORY_SELFIE, _("Selfie")),
        (CATEGORY_PANORAMA, _("Parnorama")),
        (CATEGORY_BURST, _("Burst")),
        (CATEGORY_SCREENSHOT, _("Screenshot")),
        (CATEGORY_VIDEO, _("Video")),
        (CATEGORY_VIDEO_INTERVAL, _("Interval video")),
        (CATEGORY_VIDEO_SLOMO, _("Slo-mo video")),
        (CATEGORY_VIDEO_WIDESCREEN, _("Widescreen video")),
        (CATEGORY_NON_MEDIA, _("Not image or video")),
        (CATEGORY_MEDIA_PORTRAIT, _("Portrait media")),
        (CATEGORY_MEDIA_LANDSCAPE, _("Landscape media")),
        (CATEGORY_MEDIA_SQUARE, _("Square media")),
    )
