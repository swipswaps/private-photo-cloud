import logging

from processing.processor import DataProcessor

PROCESSORS = (
    'processing.groups.by_shot_at.GroupMediaByShotAt',
    # TODO: Group SDR + HDR
    # TODO: Group bursts
)


def run(media_id=None):
    logger = logging.getLogger(__name__)
    logger.info('group media starting Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)
