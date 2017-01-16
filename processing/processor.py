import inspect
import pydoc
import types


class DataProcessor:
    PROCESSORS_DATA = ()
    ARGS = ()
    ALL_ARGUMENTS = {'ALL'}
    INITIAL_STATE_ARG = 'INITIAL_STATE'
    logger = None

    def __init__(self, processors, logger=None):
        self.logger = logger
        # TODO: Maybe initialize once on application startup

        processors_fns = [(pydoc.locate(path), path) for path in processors]

        missing_processors = [path for fn, path in processors_fns if not fn]
        assert not missing_processors, 'Some processors are missing: %r' % (missing_processors)

        processors_args = ((inspect.getfullargspec(fn), fn, path) for fn, path in processors_fns)

        self.PROCESSORS_DATA = [
            (((set(args.args) - {'self', 'cls'}) if not args.varkw else self.ALL_ARGUMENTS), fn, path)
            for args, fn, path in processors_args
            ]

        self.ARGS = {arg for args, fn, path in self.PROCESSORS_DATA for arg in args}

    def run(self, **kwargs):
        data = {**kwargs, 'ARGS': self.ARGS}

        results = ()

        self.logger.info('INPUT: %r', kwargs)

        for i, (args, fn, path) in enumerate(self.PROCESSORS_DATA):
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
                self.logger.error('%s: %r', path, ex)
                raise

            data.update(results)

            if i:
                # skip results for first iteraton
                self.logger.info('%s: %r', path, results)

        # Return not all intermediary variables but result of last command
        # If you want to -- you could make your last command to return all variables
        return dict(results) if results else None