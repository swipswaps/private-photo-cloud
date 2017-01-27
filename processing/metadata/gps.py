import re

from storage.helpers import get_re_keys_filled_value


def dms_dict2dd(degrees=0, minutes=0, seconds=0, direction='N'):
    """
    >>> dms_dict2dd(degrees='51', minutes='50', seconds='20.13', direction='N')
    51.838925
    >>> dms_dict2dd(degrees='51', minutes='50', seconds='20.13', direction=None)
    51.838925
    """
    dd = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    return -dd if direction in ('S', 'W') else dd


RE_DMS = re.compile(
    r'''^(?P<degrees>\d+)\s*(deg|°)\s*(?P<minutes>\d+)\s*'\s*(?P<seconds>\d+([.]\d+)?)\s*"\s*(?P<direction>[NSEW])?$'''
)


def parse_dms(text):
    """
    >>> parse_dms('51 deg 50\' 20.13" N')
    {'degrees': '51', 'minutes': '50', 'seconds': '20.13', 'direction': 'N'}
    >>> parse_dms('51 deg 50\' 20.13"')
    {'degrees': '51', 'minutes': '50', 'seconds': '20.13', 'direction': None}
    """
    m = RE_DMS.search(text)
    if not m:
        return
    return m.groupdict()


def dms2dd(text):
    """
    >>> dms2dd('51 deg 50\' 20.13" N')
    51.838925
    >>> dms2dd('51 deg 50\' 20.13"')
    51.838925
    """
    if not text:
        return

    m = parse_dms(text)
    if m:
        return dms_dict2dd(**m)


RE_ALTITUDE = re.compile(r'^(?i)(?P<meters>[-]?\d+([.]\d+)?)\s*m\s*(Above Sea Level)?$')


def alt2m(text):
    """
    >>> alt2m('48.33654877 m')
    48.33654877
    >>> alt2m('48.3 m Above Sea Level')
    48.3
    """
    if not text:
        return

    m = RE_ALTITUDE.search(text)
    if m:
        return float(m.group('meters'))


class GPSByExiftoolMetadata:
    RE_LATITUDE = re.compile('(?i)GPSLatitude$')    # Composite:GPSLatitude  | EXIF:GPSLatitude
    RE_LONGITUDE = re.compile('(?i)GPSLongitude$')  # Composite:GPSLongitude | EXIF:GPSLongitude
    RE_ALTITUDE = re.compile('(?i)GPSAltitude$')    # Composite:GPSAltitude  | EXIF:GPSAltitude

    @staticmethod
    def run(metadata):
        if not metadata.get('exiftool'):
            return

        return {
            'gps_latitude': dms2dd(get_re_keys_filled_value(metadata['exiftool'], GPSByExiftoolMetadata.RE_LATITUDE)),
            'gps_longitude': dms2dd(get_re_keys_filled_value(metadata['exiftool'], GPSByExiftoolMetadata.RE_LONGITUDE)),
            'gps_altitude_m': alt2m(get_re_keys_filled_value(metadata['exiftool'], GPSByExiftoolMetadata.RE_ALTITUDE)),
        }
