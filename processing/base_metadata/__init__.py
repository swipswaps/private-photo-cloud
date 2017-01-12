import inspect
import logging
import pydoc
import types

logger = logging.getLogger(__name__)

PROCESSORS = (
    'processing.base_metadata.filetype.MimetypeByContent',
    'processing.base_metadata.filetype.MediatypeByMimeType',
    'processing.base_metadata.filetype.ImageMetadataByContent',
    'processing.base_metadata.filetype.ImageMimetypeByMetadata',
    'processing.base_metadata.filetype.ImageDegreeByMetadata.run',
)


class MediaProcessor:
    PROCESSORS = ()
    INPUT_FIELDS = ()

    def __init__(self, processors):
        self.PROCESSORS = [
            (path, fn, set(inspect.getfullargspec(fn).args) - {'self', 'cls'})
            for path, fn in ((p, pydoc.locate(p)) for p in processors)
            ]

        self.INPUT_FIELDS = {f for path, fn, fields in self.PROCESSORS for f in fields}

    def __call__(self, media):
        logger.info('extract base metadata for Media.id=%s', media.id)

        data = {k: getattr(media, k) for k in self.INPUT_FIELDS}

        for path, fn, fields in self.PROCESSORS:
            try:
                results = fn(**{k: data[k] for k in fields})

                if not results:
                    continue
                elif isinstance(results, types.GeneratorType):
                    # iterate over each "yield" -> run all code to catch all exceptions
                    results = tuple(results)
                else:
                    # result is a tuple: (k, v)
                    results = (results,)
            except Exception as ex:
                logger.error('%s: %r', path, ex)
                continue

            for k, v in results:
                logger.info('%s: %s=%r', path, k, v)
                data[k] = v

                # TODO: Save into media final result


def run(media):
    MediaProcessor(PROCESSORS)(media)
