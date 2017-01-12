import logging

logger = logging.getLogger(__name__)


def run(media_id=None):
    logger.info('generate play media for Media.id=%s', media_id)
    # TODO: Mark media as ready for "play"
    # TODO: Implement pipeline / middleware
