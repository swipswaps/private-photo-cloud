import logging

from processing.processor import DataProcessor

logger = logging.getLogger(__name__)

PROCESSORS = (
    'processing.base_metadata.common.get_media_by_id',

    'processing.base_metadata.common.MimetypeByContent',
    'processing.base_metadata.common.MediatypeByMimeType',
    'processing.base_metadata.common.ExiftoolMetadataByContent',
    'processing.base_metadata.common.MimetypeByExiftoolMetadata',

    'processing.base_metadata.image.DegreeByExiftoolMetadata',
    'processing.base_metadata.image.SizeCameraByExiftoolMetadata',
    'processing.base_metadata.image.ShotAtByExiftoolMetadata',

    'processing.base_metadata.video.FfprobeMetadataByContent',
    'processing.base_metadata.video.DurationSizeByFfprobeMetadata',
    'processing.base_metadata.video.DegreeByFfprobeMetadata',
    'processing.base_metadata.video.CameraByFfprobeMetadata',
    'processing.base_metadata.video.ShotAtByFfprobeMetadata',

    'processing.base_metadata.common.ShowAtByShotAtSourceLastModified',

    'processing.base_metadata.common.ContentByExtensionShowAt.run',  # that must go RIGHT before `save_media`
    'processing.base_metadata.common.save_media',
)


def run(media_id=None):
    # E.g. touch manage.py && ./manage.sh shell -c 'from processing import tasks; tasks.extract_base_metadata(814)'
    logger.info('extract base metadata for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)

    # TODO: Maybe generate SHA1 for binary content, though it is usually re-compressed on metadata removal
