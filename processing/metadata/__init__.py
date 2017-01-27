import logging

from processing.processor import DataProcessor

PROCESSORS = (
    'processing.media_processors.get_media_by_id',

    'processing.metadata.gps.GPSByExiftoolMetadata.run',

    'processing.media_processors.save_media',
)


def run(media_id=None):
    logger = logging.getLogger(__name__)
    logger.info('calculate metadata for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)
