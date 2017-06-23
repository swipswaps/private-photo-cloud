import logging

from processing.processor import DataProcessor


PROCESSORS = (
    # TODO: Implement
)


def run(media_id=None):
    logger = logging.getLogger(__name__)
    logger.info('generate play media for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)
    # TODO: Mark media as ready for "play"
    """Optimize media for web, e.g. transcode video (multiple codecs) and pack images, find good screenshot"""
    """Extract screenshot of the video"""
    # See http://superuser.com/questions/538112/meaningful-thumbnails-for-a-video-using-ffmpeg
    # TODO: Implement generating content, optimized for viewing in browser, e.g. max 2880 x 1800, jpeg / mp4
    # TODO: Consider generating "original rotated" media, identical with quality but ready for usage
