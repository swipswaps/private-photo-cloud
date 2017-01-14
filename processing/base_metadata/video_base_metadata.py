import datetime

from storage.helpers import resolve_dict, get_first_filled_value
from storage.tools import ffmpeg


class VideoMetadataConst:
    KEYS_VIDEO_SHOOT = (
        'format:tags:com.apple.quicktime.creationdate',
        'format:tags:creation_time',
    )

    @classmethod
    def is_video(cls, media_type=None):
        from storage.const import MediaConstMixin
        return media_type == MediaConstMixin.MEDIA_VIDEO


def MetadataByContent(media_type=None, content=None):
    if not VideoMetadataConst.is_video(media_type=media_type):
        return

    return 'metadata', ffmpeg.get_ffprobe_info(content.path)


def get_get_video_stream(metadata=None):
    video_streams = [stream for stream in metadata['streams'] if stream['codec_type'] == 'video']

    if len(video_streams) == 1:
        return video_streams[0]
    elif not video_streams:
        raise ValueError('Video file has no video streams')
    raise NotImplementedError(f'Multi-stream videos ({len(video_streams)} streams) are not supported')


def DurationSizeByMetadata(media_type=None, metadata=None):
    if not VideoMetadataConst.is_video(media_type=media_type):
        return

    video_stream = get_get_video_stream(metadata=metadata)

    yield 'duration', datetime.timedelta(seconds=float(video_stream['duration']))

    width = video_stream["width"]
    height = video_stream["height"]

    assert width and height

    yield 'width', width
    yield 'height', height


def DegreeByMetadata(media_type=None):
    if not VideoMetadataConst.is_video(media_type=media_type):
        return

    # videos are auto-rotated by ffmpeg during playout / screenshot extraction, so no rotation needed
    # OLD: video_stream['side_data_list'][0]['rotation'] OR video_stream['tags']['rotate']
    return 'needed_rotate_degree', 0


def CameraByMetadata(media_type=None, metadata=None):
    if not VideoMetadataConst.is_video(media_type=media_type):
        return

    yield 'camera', resolve_dict('format:tags:com.apple.quicktime.model', metadata) or ''


def get_shot_dates(metadata=None):
    for path in VideoMetadataConst.KEYS_VIDEO_SHOOT:
        yield resolve_dict(path, metadata)

    # try all streams
    for stream in metadata["streams"]:
        yield resolve_dict('tags.creation_time', stream)


def ShotAtByMetadata(media_type=None, metadata=None):
    from processing.base_metadata.image_base_metadata import parse_shot_at

    if not VideoMetadataConst.is_video(media_type=media_type):
        return

    shot_date = get_first_filled_value(get_shot_dates(metadata=metadata))

    if shot_date:
        return 'shot_at', parse_shot_at(shot_date)
