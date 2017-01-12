import logging

logger = logging.getLogger(__name__)


def run(media_id=None):
    logger.info('categorize for Media.id=%s', media_id)
    # TODO: Implement pipeline / middleware
