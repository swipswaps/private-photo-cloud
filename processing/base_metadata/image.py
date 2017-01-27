import datetime
import re

from django.utils import timezone

from processing.media_processors import is_image
from storage.helpers import get_keys_filled_value


class DegreeByExiftoolMetadata:
    KEYS_IMAGE_ORIENTATION = (
        'EXIF:Orientation',
        'MakerNotes:CameraOrientation',
    )

    ORIENTATIONS_NO_DEGREE = {
        'Horizontal (normal)': 0,
    }

    RE_ORIENTATION = re.compile(r'^Rotate (?P<degree>\d+)(?P<counter> CW)?$')

    @staticmethod
    def run(media_type=None, metadata=None):
        if not is_image(media_type=media_type):
            return

        orientation = get_keys_filled_value(metadata['exiftool'], DegreeByExiftoolMetadata.KEYS_IMAGE_ORIENTATION)

        if not orientation:
            # Was not found -- prompt user to rotate
            return 'needed_rotate_degree', None

        try:
            # First check exact match
            return 'needed_rotate_degree', DegreeByExiftoolMetadata.ORIENTATIONS_NO_DEGREE[orientation]
        except KeyError:
            pass

        # Try to parse orientation
        m = DegreeByExiftoolMetadata.RE_ORIENTATION.search(orientation)

        if not m:
            # Failed to parse
            raise NotImplementedError(f'Unsupported orientation: {orientation}')

        degree = int(m.group('degree'), 10)

        if m.group('counter'):
            # counter-clockwise
            return 'needed_rotate_degree', degree

        # clock-wise
        return 'needed_rotate_degree', 360 - degree


class SizeCameraByExiftoolMetadata:
    KEYS_IMAGE_CAMERA = (
        'EXIF:Model',
        'MakerNotes:CanonImageType',
        'MakerNotes:CanonModelID',
    )

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

    @staticmethod
    def run(media_type=None, metadata=None):
        if not is_image(media_type=media_type):
            return

        yield 'camera', get_keys_filled_value(metadata['exiftool'], SizeCameraByExiftoolMetadata.KEYS_IMAGE_CAMERA) or ''

        width = get_keys_filled_value(metadata['exiftool'], SizeCameraByExiftoolMetadata.KEYS_IMAGE_WIDTH)
        height = get_keys_filled_value(metadata['exiftool'], SizeCameraByExiftoolMetadata.KEYS_IMAGE_HEIGHT)

        assert width and height

        yield 'width', width
        yield 'height', height


class ShotDate:
    SHOOT_DATE_FORMATS = (
        '%Y:%m:%d %H:%M:%S',  # 2016:10:19 21:08:00
        '%Y:%m:%d %H:%M:%S.%f',  # 2016:11:06 14:29:25.018
        '%Y-%m-%dT%H:%M:%S%z',  # 2016-10-22T14:39:13+0200
    )

    @staticmethod
    def parse(value):
        # Fix too short microseconds section (14:29:25.018 => 14:29:25.01800)
        value = re.sub(r'(?<=[.])(\d+)$', lambda m: m.group(1).ljust(6, '0'), value)

        for dt_format in ShotDate.SHOOT_DATE_FORMATS:
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


class ShotAtByExiftoolMetadata:
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

    @staticmethod
    def run(media_type=None, metadata=None):
        if not is_image(media_type=media_type):
            return

        shot_date = get_keys_filled_value(metadata['exiftool'], ShotAtByExiftoolMetadata.KEYS_IMAGE_SHOOT)

        if shot_date:
            return 'shot_at', ShotDate.parse(shot_date)
