from processing import tasks


class ProcessingState:
    STATUS_CODE = None
    NEXT_TASK = None

    @classmethod
    def run(cls, media_id):
        from storage.models import Media
        media = Media.objects.get(pk=media_id)

        fn = cls.get_exec_method(media)
        fn(media)

        media.processing_state_code = cls.STATUS_CODE
        media.save()

        cls.run_next(media_id, media)

    @classmethod
    def get_exec_method(cls, media):
        raise NotImplementedError()

    @classmethod
    def run_next(cls, media_id, media):
        next_task = cls.NEXT_TASK or cls.get_next(media_id, media)

        if next_task:
            # Run next task asynchronously
            next_task.delay(media_id)

    @classmethod
    def get_next(cls, media_id, media):
        raise NotImplementedError()

class InitialState(ProcessingState):
    NEXT_TASK = tasks.extract_base_metadata
    @classmethod
    def run(cls, media_id):
        cls.run_next(media_id, None)

    @classmethod
    def run_next(cls, media_id, media):
        # Run immediately
        cls.NEXT_TASK(media_id)


class ExtractBaseMetadataState(ProcessingState):
    STATUS_CODE = 1
    NEXT_TASK = tasks.generate_quick_thumbnail

    @classmethod
    def get_exec_method(cls, media):
        from processing.base_metadata import run
        return run


class GenerateQuickThumbnailState(ProcessingState):
    STATUS_CODE = 2
    NEXT_TASK = tasks.generate_play

    @classmethod
    def get_exec_method(cls, media):
        from processing.quick_thumbnail import run
        return run


class GeneratePlayState(ProcessingState):
    STATUS_CODE = 3
    NEXT_TASK = tasks.calculate_metadata

    @classmethod
    def get_exec_method(cls, media):
        from processing.play_media import run
        return run


class CalculateMetadataState(ProcessingState):
    STATUS_CODE = 4
    NEXT_TASK = tasks.categorize

    @classmethod
    def get_exec_method(clss, media):
        from processing.metadata import run
        return run


class CategorizeState(ProcessingState):
    STATUS_CODE = 5
    NEXT_TASK = None

    @classmethod
    def get_next(cls, media_id, media):
        # nothing to do next
        return None

    @classmethod
    def get_exec_method(cls, media):
        from processing.categories import run
        return run
