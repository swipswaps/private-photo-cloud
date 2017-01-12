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
    'processing.base_metadata.filetype.ImageDegreeByMetadata',
    'processing.base_metadata.filetype.SizeCameraByMetadata',
    'processing.base_metadata.filetype.DateBySource',
    'processing.base_metadata.filetype.DateByMetadata',
    'processing.base_metadata.save_media',
)


def get_media_by_id(media_id=None, ARGS=None):
    from storage.models import Media

    # exclude arguments of this method
    ARGS = set(ARGS) - set(inspect.getfullargspec(get_media_by_id).args) - DataProcessor.ALL_ARGUMENTS

    media = Media.objects.filter(id=media_id).only(*ARGS).get()
    media = {k: getattr(media, k) for k in ARGS}

    yield DataProcessor.INITIAL_STATE_ARG, media
    yield from media.items()


def save_media(ARGS=None, media_id=None, **kwargs):
    from storage.models import Media

    initial_state = kwargs.pop(DataProcessor.INITIAL_STATE_ARG)
    data = {k: v for k, v in kwargs.items() if v is not initial_state.get(k)}

    media = Media.objects.filter(id=media_id).only('id').get()

    for k, v in data.items():
        setattr(media, k, v)

    media.save(update_fields=data)

    return 'media', media


class DataProcessor:
    PROCESSORS = ()
    ARGS = ()
    ALL_ARGUMENTS = {'ALL'}
    INITIAL_STATE_ARG = 'INITIAL_STATE'

    def __init__(self, processors):
        # TODO: Maybe initialize once on application startup

        processors_fns = ((pydoc.locate(p), p) for p in processors)
        processors_args = ((inspect.getfullargspec(fn), fn, path) for fn, path in processors_fns)

        self.PROCESSORS = [
            (((set(args.args) - {'self', 'cls'}) if not args.varkw else self.ALL_ARGUMENTS), fn, path)
            for args, fn, path in processors_args
            ]

        self.ARGS = {arg for args, fn, path in self.PROCESSORS for arg in args}

    def run(self, **kwargs):
        data = {**kwargs, 'ARGS': self.ARGS}

        results = ()

        for args, fn, path in self.PROCESSORS:
            input_data = data if args is self.ALL_ARGUMENTS else {k: data[k] for k in args}
            try:
                results = fn(**input_data)

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
                if k != DataProcessor.INITIAL_STATE_ARG:
                    logger.info('%s: %s=%r', path, k, v)
                data[k] = v

        # Return not all intermediary variables but result of last command
        # If you want to -- you could make your last command to return all variables
        return dict(results) if results else None


def run(media_id=None):
    # E.g. touch manage.py && ./manage.sh shell -c 'from processing import tasks; tasks.extract_base_metadata(814)'
    logger.info('extract base metadata for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS).run(media_id=media_id)
    logger.info('result: %r', result)
