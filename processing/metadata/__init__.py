import logging

logger = logging.getLogger(__name__)


def run(media_id=None):
    logger.info('calculate metadata for Media.id=%s', media_id)
    # TODO: Implement pipeline / middleware
