import inspect
import logging
import pydoc
import types

logger = logging.getLogger(__name__)

PROCESSORS = (
    'processing.base_metadata.common.get_media_by_id',

    'processing.base_metadata.common.MimetypeByContent',
    'processing.base_metadata.common.MediatypeByMimeType',
    'processing.base_metadata.common.ExiftoolMetadataByContent',
    'processing.base_metadata.common.MimetypeByExiftoolMetadata',

    'processing.base_metadata.image.DegreeByExiftoolMetadata',
    'processing.base_metadata.image.SizeCameraByExiftoolMetadata',
    'processing.base_metadata.image.ShotAtByExiftoolMetadata',

    'processing.base_metadata.video.FfprobeMetadataByContent',
    'processing.base_metadata.video.DurationSizeByFfprobeMetadata',
    'processing.base_metadata.video.DegreeByFfprobeMetadata',
    'processing.base_metadata.video.CameraByFfprobeMetadata',
    'processing.base_metadata.video.ShotAtByFfprobeMetadata',

    'processing.base_metadata.common.ShowAtByShotAtSourceLastModified',

    'processing.base_metadata.common.ContentByExtensionShowAt.run',  # that must go RIGHT before `save_media`
    'processing.base_metadata.common.save_media',
)


class DataProcessor:
    PROCESSORS = ()
    ARGS = ()
    ALL_ARGUMENTS = {'ALL'}
    INITIAL_STATE_ARG = 'INITIAL_STATE'

    def __init__(self, processors):
        # TODO: Maybe initialize once on application startup

        processors_fns = [(pydoc.locate(path), path) for path in processors]

        missing_processors = [path for fn, path in processors_fns if not fn]
        assert not missing_processors, 'Some processors are missing: %r' % (missing_processors)

        processors_args = ((inspect.getfullargspec(fn), fn, path) for fn, path in processors_fns)

        self.PROCESSORS = [
            (((set(args.args) - {'self', 'cls'}) if not args.varkw else self.ALL_ARGUMENTS), fn, path)
            for args, fn, path in processors_args
            ]

        self.ARGS = {arg for args, fn, path in self.PROCESSORS for arg in args}

    def run(self, **kwargs):
        data = {**kwargs, 'ARGS': self.ARGS}

        results = ()

        logger.info('INPUT: %r', kwargs)

        for i, (args, fn, path) in enumerate(self.PROCESSORS):
            input_data = data if args is self.ALL_ARGUMENTS else {k: data[k] for k in args}
            try:
                results = fn(**input_data)

                if isinstance(results, types.GeneratorType):
                    # iterate over each "yield" -> run all code to catch all exceptions
                    results = dict(results)

                if not results:
                    # Nothing to do, go to the next processor
                    continue
                elif not isinstance(results, dict):
                    # result is a tuple: (k, v)
                    results = {results[0]: results[1]}
            except Exception as ex:
                logger.error('%s: %r', path, ex)
                raise

            data.update(results)

            if i:
                # skip results for first iteraton
                logger.info('%s: %r', path, results)

        # Return not all intermediary variables but result of last command
        # If you want to -- you could make your last command to return all variables
        return dict(results) if results else None


def run(media_id=None):
    # E.g. touch manage.py && ./manage.sh shell -c 'from processing import tasks; tasks.extract_base_metadata(814)'
    logger.info('extract base metadata for Media.id=%s', media_id)
    result = DataProcessor(PROCESSORS).run(media_id=media_id)

    # TODO: Maybe generate SHA1 for binary content, though it is usually re-compressed on metadata removal
