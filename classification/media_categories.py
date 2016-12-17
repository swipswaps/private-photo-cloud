import logging

logger = logging.getLogger(__name__)

# "aspect ratio of 2:1 or larger" -- @https://en.wikipedia.org/wiki/Panoramic_photography
IMAGE_PANORAMA_ASPECT = 2  #

# 2.35 / 2.39 / 2.40 -- @https://en.wikipedia.org/wiki/Anamorphic_format#2.35.2C_2.39_or_2.40.3F
VIDEO_WIDESCREEN_ASPECT = 2  # maybe 2.35


def get(media):
    if media.media_type == media.MEDIA_OTHER or not media.thumbnail_width or not media.thumbnail_height:
        # Not a media or unable to generate thumbnail
        yield media.CATEGORY_NON_MEDIA
        return

    if media.media_type == media.MEDIA_VIDEO:
        yield media.CATEGORY_VIDEO
    elif media.media_type == media.MEDIA_IMAGE:
        yield media.CATEGORY_IMAGE
    else:
        raise NotImplementedError(media.media_type)

    # Use thumbnail resolution since we don't need high precision and it is rotated
    width, height = media.thumbnail_width, media.thumbnail_height

    if width == height:
        yield media.CATEGORY_MEDIA_SQUARE
    elif width > height:
        yield media.CATEGORY_MEDIA_LANDSCAPE
    else:
        yield media.CATEGORY_MEDIA_PORTRAIT

    if media.media_type == media.MEDIA_IMAGE:
        if IMAGE_PANORAMA_ASPECT <= (width / height):
            yield media.CATEGORY_PANORAMA
    elif media.media_type == media.MEDIA_VIDEO:
        if VIDEO_WIDESCREEN_ASPECT <= (width / height):
            yield media.CATEGORY_VIDEO_WIDESCREEN

    """
    TODO:
    * CATEGORY_SELFIE
    * CATEGORY_BURST
    * CATEGORY_SCREENSHOT
    * CATEGORY_VIDEO_INTERVAL
    * CATEGORY_VIDEO_SLOMO
    """
