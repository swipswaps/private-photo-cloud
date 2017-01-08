import logging

logger = logging.getLogger(__name__)


def run(media):
    logger.info('generate play media for Media.id=%s', media.id)
    # TODO: Mark media as ready for "play"
    # TODO: Implement pipeline / middleware
