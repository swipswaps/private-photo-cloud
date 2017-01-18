import logging

from processing.processor import DataProcessor

PROCESSORS = (
    # TODO: Implement
)


def run(media_id=None):
    logger = logging.getLogger(__name__)
    logger.info('calculate metadata for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)
