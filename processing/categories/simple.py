from processing.media_processors import is_image, is_video
from storage.const import MediaConstMixin


def CategoriesToSet(categories=None):
    return 'categories', set(categories) if categories else set()


def CategoriesToTuple(categories=None):
    return 'categories', tuple(categories) if categories else ()



def get_aspect_ratio_absolute(width, height):
    if width and height:
        return (width / height) if width > height else (height / width)


class CategoryTypeByMediaType:
    CATEGORY_BY_TYPE = {
        MediaConstMixin.MEDIA_IMAGE: MediaConstMixin.CATEGORY_IMAGE,
        MediaConstMixin.MEDIA_VIDEO: MediaConstMixin.CATEGORY_VIDEO,
        MediaConstMixin.MEDIA_OTHER: MediaConstMixin.CATEGORY_NON_MEDIA,
    }

    @staticmethod
    def run(media_type=None, categories=None):
        return 'categories', categories | {CategoryTypeByMediaType.CATEGORY_BY_TYPE[media_type]}


def CategoryAspectRatioByThumbnailSize(categories=None, thumbnail_width=None, thumbnail_height=None):
    if not thumbnail_width or not thumbnail_height:
        return 'categories', categories | {MediaConstMixin.CATEGORY_NON_MEDIA}

    aspect_ratio = thumbnail_width / thumbnail_height

    if aspect_ratio == 1:
        return 'categories', categories | {MediaConstMixin.CATEGORY_MEDIA_SQUARE}
    elif aspect_ratio > 1:
        return 'categories', categories | {MediaConstMixin.CATEGORY_MEDIA_LANDSCAPE}

    return 'categories', categories | {MediaConstMixin.CATEGORY_MEDIA_PORTRAIT}


def CategoryPanoramaByThumbnailSize(categories=None, media_type=None, thumbnail_width=None, thumbnail_height=None):
    aspect_ratio = get_aspect_ratio_absolute(thumbnail_width, thumbnail_height)

    # "aspect ratio of 2:1 or larger" -- @https://en.wikipedia.org/wiki/Panoramic_photography
    if is_image(media_type) and aspect_ratio and 2 <= aspect_ratio:
        return 'categories', categories | {MediaConstMixin.CATEGORY_PANORAMA}


def CategoryWidescreenByThumbnailSize(categories=None, media_type=None, thumbnail_width=None, thumbnail_height=None):
    aspect_ratio = get_aspect_ratio_absolute(thumbnail_width, thumbnail_height)

    # 2.35 / 2.39 / 2.40 -- @https://en.wikipedia.org/wiki/Anamorphic_format#2.35.2C_2.39_or_2.40.3F
    if is_video(media_type) and aspect_ratio and 2 <= aspect_ratio:  # maybe 2.35
        return 'categories', categories | {MediaConstMixin.CATEGORY_VIDEO_WIDESCREEN}
