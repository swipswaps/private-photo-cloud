import datetime
import re

from django.utils import timezone

from storage.const import MediaConstMixin
from storage.helpers import get_first_filled_key


class MetadataConst:
    TYPES = {
        'image': MediaConstMixin.MEDIA_IMAGE,
        'video': MediaConstMixin.MEDIA_VIDEO,
    }
    TYPE_DEFAULT = MediaConstMixin.MEDIA_OTHER
    KEY_MIMETYPE = 'File:MIMEType'

    KEYS_IMAGE_ORIENTATION = (
        'EXIF:Orientation',
        'MakerNotes:CameraOrientation',
    )

    ORIENTATIONS_NO_DEGREE = {
        'Horizontal (normal)': 0,
    }

    KEYS_IMAGE_CAMERA = (
        'EXIF:Model',
        'MakerNotes:CanonImageType',
        'MakerNotes:CanonModelID',
    )

    RE_ORIENTATION = re.compile(r'^Rotate (?P<degree>\d+)(?P<counter> CW)?$')

    KEYS_IMAGE_WIDTH = (
        "File:ImageWidth",
        'PNG:ImageWidth',
        "EXIF:ExifImageWidth",

        'MakerNotes:AFImageWidth',

        # 'MakerNotes:SensorWidth',       # ~ +40px of real size
        # 'MakerNotes:CanonImageWidth',   # about 1/2 of real size

        "EXIF:ImageWidth",  # for canon CR2 it gives 1/2, but right value for Nikon
    )

    KEYS_IMAGE_HEIGHT = (
        'File:ImageHeight',
        'PNG:ImageHeight',
        'EXIF:ExifImageHeight',

        'MakerNotes:AFImageHeight',
        'EXIF:RowsPerStrip',

        # 'MakerNotes:SensorHeight',      # ~ +28px of real size
        # 'MakerNotes:CanonImageHeight',  # about 1/2 of real size
        'EXIF:ImageHeight',  # for canon CR2 it gives 1/2, but right value for Nikon
    )

    KEYS_IMAGE_SHOOT = (
        # More precise should come first
        "Composite:SubSecCreateDate",
        "Composite:SubSecDateTimeOriginal",
        "Composite:SubSecModifyDate",
        "XMP:DateCreated",
        "EXIF:CreateDate",
        "EXIF:DateTimeOriginal",
        "EXIF:ModifyDate",
        "EXIF:GPSDateStamp",
    )

    SHOOT_DATE_FORMATS = (
        '%Y:%m:%d %H:%M:%S',  # 2016:10:19 21:08:00
        '%Y:%m:%d %H:%M:%S.%f',  # 2016:11:06 14:29:25.018
        '%Y-%m-%dT%H:%M:%S%z',  # 2016-10-22T14:39:13+0200
    )

    @classmethod
    def parse_shot_at(cls, value):
        # Fix too short microseconds section (14:29:25.018 => 14:29:25.01800)
        value = re.sub(r'(?<=[.])(\d+)$', lambda m: m.group(1).ljust(6, '0'), value)

        for dt_format in cls.SHOOT_DATE_FORMATS:
            try:
                dt = datetime.datetime.strptime(value, dt_format)
            except ValueError:
                continue

            if not dt.tzinfo:
                """
                No timezone provided -- that means date is device date:

                a) for camera -- time of home region
                b) for smartphone:
                    1) without TZ adjustment -- time of home region
                    2) with TZ adjustment -- time of current region (see GPS coordinates)

                # TODO: Implement complex logic instead of converting to server TZ.
                """
                return timezone.get_current_timezone().localize(dt, is_dst=None)
            return dt

        raise NotImplementedError(value)


def MimetypeByContent(content=None):
    import magic

    return 'mimetype', magic.from_file(content.path, mime=True)


def MediatypeByMimeType(mimetype=None):
    return 'media_type', MetadataConst.TYPES.get(mimetype.split('/')[0], MetadataConst.TYPE_DEFAULT)


def ImageMetadataByContent(media_type=None, content=None):
    from storage.tools.exiftool import get_exiftool_info

    if media_type != MediaConstMixin.MEDIA_IMAGE:
        return

    # Alternative: exiv2 (faster but less formats)
    # See: http://dev.exiv2.org/projects/exiv2/wiki/How_does_Exiv2_compare_to_Exiftool
    return 'metadata', get_exiftool_info(content.path)


def ImageMimetypeByMetadata(media_type=None, metadata=None):
    if media_type != MediaConstMixin.MEDIA_IMAGE:
        return

    mimetype = metadata.get(MetadataConst.KEY_MIMETYPE)

    if mimetype:
        # Do not overwrite if empty
        return 'mimetype', mimetype

def ImageDegreeByMetadata(media_type=None, metadata=None):
    if media_type != MediaConstMixin.MEDIA_IMAGE:
        return

    orientation = get_first_filled_key(metadata, MetadataConst.KEYS_IMAGE_ORIENTATION)

    if not orientation:
        # Was not found
        return 'needed_rotate_degree', None

    try:
        # First check exact match
        return 'needed_rotate_degree', MetadataConst.ORIENTATIONS_NO_DEGREE[orientation]
    except KeyError:
        pass

    # Try to parse orientation
    m = MetadataConst.RE_ORIENTATION.search(orientation)

    if not m:
        # Failed to parse
        raise NotImplementedError(f'Unsupported orientation: {orientation}')

    degree = int(m.group('degree'), 10)

    if m.group('counter'):
        # counter-clockwise
        return 'needed_rotate_degree', degree

    # clock-wise
    return 'needed_rotate_degree', 360 - degree


def SizeCameraByMetadata(media_type=None, metadata=None):
    if media_type != MediaConstMixin.MEDIA_IMAGE:
        return

    yield 'camera', get_first_filled_key(metadata, MetadataConst.KEYS_IMAGE_CAMERA) or ''

    width = get_first_filled_key(metadata, MetadataConst.KEYS_IMAGE_WIDTH)
    height = get_first_filled_key(metadata, MetadataConst.KEYS_IMAGE_HEIGHT)

    assert width and height

    yield 'width', width
    yield 'height', height


def DateBySource(source_lastmodified=None):
    # Default value for show_at -- override later with more precise value
    return 'show_at', source_lastmodified


def DateByMetadata(media_type=None, metadata=None):
    if media_type != MediaConstMixin.MEDIA_IMAGE:
        return

    shot_date = get_first_filled_key(metadata, MetadataConst.KEYS_IMAGE_SHOOT)

    if not shot_date:
        return

    shot_date = MetadataConst.parse_shot_at(shot_date)

    yield 'show_at', shot_date
    yield 'shot_at', shot_date
