import datetime

from processing.media_processors import is_video
from storage.helpers import resolve_dict, get_filled_value


def FfprobeMetadataByContent(media_type=None, content=None, metadata=None):
    from storage.tools import ffmpeg

    if not is_video(media_type=media_type):
        return

    # Create a clone before update -- to keep initial state immutable
    return 'metadata', dict(metadata or {}, ffprobe=ffmpeg.get_ffprobe_info(content.path))


def get_get_video_stream(streams=None):
    video_streams = [stream for stream in streams if stream['codec_type'] == 'video']

    if len(video_streams) == 1:
        return video_streams[0]
    elif not video_streams:
        raise ValueError('Video file has no video streams')
    raise NotImplementedError(f'Multi-stream videos ({len(video_streams)} streams) are not supported')


def DurationSizeByFfprobeMetadata(media_type=None, metadata=None):
    if not is_video(media_type=media_type):
        return

    video_stream = get_get_video_stream(streams=metadata['ffprobe']['streams'])

    yield 'duration', datetime.timedelta(seconds=float(video_stream['duration']))

    width = video_stream["width"]
    height = video_stream["height"]

    assert width and height

    yield 'width', width
    yield 'height', height


def DegreeByFfprobeMetadata(media_type=None):
    if not is_video(media_type=media_type):
        return

    # videos are auto-rotated by ffmpeg during playout / screenshot extraction, so no rotation needed
    # OLD: video_stream['side_data_list'][0]['rotation'] OR video_stream['tags']['rotate']
    return 'needed_rotate_degree', 0


def CameraByFfprobeMetadata(media_type=None, metadata=None):
    if not is_video(media_type=media_type):
        return

    yield 'camera', resolve_dict('format:tags:com.apple.quicktime.model', metadata['ffprobe']) or ''


class ShotAtByFfprobeMetadata:
    KEYS_VIDEO_SHOOT = (
        'format:tags:com.apple.quicktime.creationdate',
        'format:tags:creation_time',
    )

    @staticmethod
    def run(media_type=None, metadata=None):
        from processing.base_metadata.image import ShotDate

        if not is_video(media_type=media_type):
            return

        shot_date = get_filled_value(ShotAtByFfprobeMetadata.get_shot_dates(metadata=metadata['ffprobe']))

        if shot_date:
            return 'shot_at', ShotDate.parse(shot_date)

    @staticmethod
    def get_shot_dates(metadata=None):
        for path in ShotAtByFfprobeMetadata.KEYS_VIDEO_SHOOT:
            yield resolve_dict(path, metadata)

        # try all streams
        for stream in metadata["streams"]:
            yield resolve_dict('tags.creation_time', stream)
