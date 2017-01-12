import inspect
import logging
import pydoc
import types

logger = logging.getLogger(__name__)

PROCESSORS = (
    'processing.base_metadata.get_media_by_id',
    'processing.base_metadata.filetype.MimetypeByContent',
    'processing.base_metadata.filetype.MediatypeByMimeType',
    'processing.base_metadata.filetype.ImageMetadataByContent',
    'processing.base_metadata.filetype.ImageMimetypeByMetadata',
    'processing.base_metadata.filetype.ImageDegreeByMetadata.run',
)


def get_media_by_id(media_id=None, FIELDS=None):
    from storage.models import Media

    # exclude arguments of this method
    FIELDS = set(FIELDS) - {'media_id', 'FIELDS'}

    media = Media.objects.filter(id=media_id).only(*FIELDS).get()

    for k in FIELDS:
        yield k, getattr(media, k)


class DataProcessor:
    PROCESSORS = ()
    INPUT_FIELDS = ()

    def __init__(self, processors):
        # TODO: Maybe initialize once on application startup
        self.PROCESSORS = [
            (path, fn, set(inspect.getfullargspec(fn).args) - {'self', 'cls'})
            for path, fn in ((p, pydoc.locate(p)) for p in processors)
            ]

        self.INPUT_FIELDS = {f for path, fn, fields in self.PROCESSORS for f in fields}

    def run(self, **kwargs):
        data = {**kwargs, 'FIELDS': self.INPUT_FIELDS}

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


def run(media_id=None):
    logger.info('extract base metadata for Media.id=%s', media_id)
    DataProcessor(PROCESSORS).run(media_id=media_id)
