import logging

from processing.processor import DataProcessor

PROCESSORS = (
    'processing.media_processors.get_media_by_id',

    'processing.quick_thumbnail.image.ThumbnailByContentDegree',
    'processing.quick_thumbnail.image.ThumbnailByExiftoolMetadataEmbedContentDegree',

    'processing.quick_thumbnail.video.ScreenShotByDurationVideoContent.run',
    'processing.quick_thumbnail.video.ThumbnailByScreenShotDegree',

    'processing.media_processors.save_media',
)


def run(media_id=None):
    from processing.media_processors import ws_notify_about_thumbnail

    logger = logging.getLogger(__name__)
    logger.info('generate quick thumbnail for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)

    ws_notify_about_thumbnail(**result)