import logging
import pydoc
import types

logger = logging.getLogger(__name__)

CLASSES = (
    'processing.base_metadata.filetype.MimetypeByContent',
    'processing.base_metadata.filetype.MediatypeByMimeType',
    'processing.base_metadata.filetype.ImageMetadataByContent',
    'processing.base_metadata.filetype.ImageMimetypeByMetadata',
    'processing.base_metadata.filetype.ImageDegreeByMetadata',
)


class MediaProcessor:
    CLASSES = ()
    INPUT_FIELDS = ()

    def __init__(self, classes):
        self.CLASSES = tuple(map(pydoc.locate, classes))
        self.INPUT_FIELDS = {f for cls in self.CLASSES for f in cls.INPUT_FIELDS}

    def __call__(self, media):
        logger.info('extract base metadata for Media.id=%s', media.id)

        data = {k: getattr(media, k) for k in self.INPUT_FIELDS}

        for cls in self.CLASSES:
            try:
                results = cls.run(**{k: data[k] for k in cls.INPUT_FIELDS})

                if isinstance(results, types.GeneratorType):
                    # iterate over each "yield" -> run all code to catch all exceptions
                    results = tuple(results)
                else:
                    # result is a tuple: (k, v)
                    results = (results,)
            except Exception as ex:
                logger.error('Got error in %s: %r', cls, ex)
                continue

            for k, v in results:
                logger.info('Processes by %s: %s=%r', cls, k, v)
                data[k] = v

        # TODO: Save into media final result


def run(media):
    MediaProcessor(CLASSES)(media)
