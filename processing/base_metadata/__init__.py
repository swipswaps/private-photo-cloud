import logging

from processing.processor import DataProcessor

PROCESSORS = (
    'processing.media_processors.get_media_by_id',

    'processing.base_metadata.common.MimetypeByContent',
    'processing.base_metadata.common.MediatypeByMimeType.run',
    'processing.base_metadata.common.ExiftoolMetadataByContent',
    'processing.base_metadata.common.MimetypeByExiftoolMetadata',

    'processing.base_metadata.image.DegreeByExiftoolMetadata.run',
    'processing.base_metadata.image.SizeCameraByExiftoolMetadata.run',
    'processing.base_metadata.image.ShotAtByExiftoolMetadata.run',

    'processing.base_metadata.video.FfprobeMetadataByContent',
    'processing.base_metadata.video.DurationSizeByFfprobeMetadata',
    'processing.base_metadata.video.DegreeByFfprobeMetadata',
    'processing.base_metadata.video.CameraByFfprobeMetadata',
    'processing.base_metadata.video.ShotAtByFfprobeMetadata.run',

    'processing.base_metadata.common.ShowAtByShotAtSourceLastModified',
    'processing.base_metadata.common.ContentByExtensionShowAt.run',  # that must go RIGHT before `save_media`

    'processing.media_processors.save_media',
)


def run(media_id=None):
    # E.g. touch manage.py && ./manage.sh shell -c 'from processing import tasks; tasks.extract_base_metadata(814)'
    logger = logging.getLogger(__name__)
    logger.info('extract base metadata for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)

    # TODO: Maybe generate SHA1 for binary content, though it is usually re-compressed on metadata removal
