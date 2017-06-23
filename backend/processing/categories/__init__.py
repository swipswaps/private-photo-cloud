import logging

from processing.processor import DataProcessor

"""
TODO:
* CATEGORY_SELFIE
* CATEGORY_BURST
* CATEGORY_SCREENSHOT
* CATEGORY_VIDEO_INTERVAL
* CATEGORY_VIDEO_SLOMO
"""
# TODO: Add more classification
# TODO: Mark media with tags, e.g. "RAW", "Orig", "HDR", "Modified"


PROCESSORS = (
    'processing.media_processors.get_media_by_id',
    'processing.categories.simple.EmptyCategories',

    'processing.categories.simple.CategoryTypeByMediaType.run',
    'processing.categories.simple.CategoryAspectRatioByThumbnailSize',
    'processing.categories.simple.CategoryPanoramaByThumbnailSize',
    'processing.categories.simple.CategoryWidescreenByThumbnailSize',

    'processing.categories.simple.CategoriesToTuple',
    'processing.media_processors.save_media',
)


def run(media_id=None):
    logger = logging.getLogger(__name__)
    logger.info('categorize for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS, logger=logger).run(media_id=media_id)
