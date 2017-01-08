import logging

logger = logging.getLogger(__name__)


def run(media):
    logger.info('categorize for Media.id=%s', media.id)
    # TODO: Implement pipeline / middleware
