import logging

logger = logging.getLogger(__name__)


def run(media_id=None):
    logger.info('generate quick thumbnail for Media.id=%s', media_id)
    # TODO: Implement pipeline / middleware
