import re

from storage.const import MediaConstMixin
from storage.helpers import get_first_filled_key


def MimetypeByContent(content=None):
    import magic

    return 'mimetype', magic.from_file(content.path, mime=True)


def MediatypeByMimeType(mimetype=None):
    mimetype = mimetype.split('/')[0]

    TYPES = {
        'image': MediaConstMixin.MEDIA_IMAGE,
        'video': MediaConstMixin.MEDIA_VIDEO,
    }

    return 'media_type', TYPES.get(mimetype, MediaConstMixin.MEDIA_OTHER)


def ImageMetadataByContent(media_type=None, content=None):
    from storage.tools.exiftool import get_exiftool_info

    if media_type != MediaConstMixin.MEDIA_IMAGE:
        return

    # Alternative: exiv2 (faster but less formats)
    # See: http://dev.exiv2.org/projects/exiv2/wiki/How_does_Exiv2_compare_to_Exiftool
    return 'metadata', get_exiftool_info(content.path)


class ImageMimetypeByMetadata:
    IMAGE_MIMETYPE_KEYS = (
        'File:MIMEType',
    )

    @classmethod
    def run(cls, media_type=None, metadata=None):
        if media_type != MediaConstMixin.MEDIA_IMAGE:
            return

        return 'mimetype', get_first_filled_key(metadata, cls.IMAGE_MIMETYPE_KEYS)


class ImageDegreeByMetadata:
    IMAGE_ORIENTATION_KEYS = (
        'EXIF:Orientation',
        'MakerNotes:CameraOrientation',
    )

    ORIENTATIONS_NO_DEGREE = {
        'Horizontal (normal)': 0,
    }

    RE_ORIENTATION = re.compile(r'^Rotate (?P<degree>\d+)(?P<counter> CW)?$')

    @classmethod
    def run(cls, media_type=None, metadata=None):
        if media_type != MediaConstMixin.MEDIA_IMAGE:
            return

        orientation = get_first_filled_key(metadata, cls.IMAGE_ORIENTATION_KEYS)

        if not orientation:
            # Was not found
            return 'needed_rotate_degree', None

        try:
            # First check exact match
            return 'needed_rotate_degree', cls.ORIENTATIONS_NO_DEGREE[orientation]
        except KeyError:
            pass

        # Try to parse orientation
        m = cls.RE_ORIENTATION.search(orientation)

        if not m:
            # Failed to parse
            raise NotImplementedError(f'Unsupported orientation: {orientation}')

        degree = int(m.group('degree'), 10)

        if m.group('counter'):
            # counter-clockwise
            return 'needed_rotate_degree', degree

        # clock-wise
        return 'needed_rotate_degree', 360 - degree
