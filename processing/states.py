import pydoc
from collections import namedtuple

State = namedtuple('State', ['code', 'task', 'command'])


class ProcessingState:
    STATE_INITIAL = 0
    STATE_BASE_METADATA = 1
    STATE_QUICK_THUMBNAIL = 2
    STATE_PLAY_MEDIA = 3
    STATE_METADATA = 4
    STATE_CATEGORIES = 5

    STATES = (
        State(STATE_INITIAL, 'processing.tasks.initial_state', None),
        State(STATE_BASE_METADATA, 'processing.tasks.extract_base_metadata', 'processing.base_metadata.run'),
        State(STATE_QUICK_THUMBNAIL, 'processing.tasks.generate_quick_thumbnail', 'processing.quick_thumbnail.run'),
        State(STATE_PLAY_MEDIA, 'processing.tasks.generate_play', 'processing.play_media.run'),
        State(STATE_METADATA, 'processing.tasks.calculate_metadata', 'processing.metadata.run'),
        State(STATE_CATEGORIES, 'processing.tasks.categorize', 'processing.categories.run'),
    )

    @classmethod
    def run(cls, state_code, media_id):
        from storage.models import Media

        # create iterator to be able to find "next" state
        states = iter(cls.STATES)
        state = next((state for state in states if state.code == state_code), None)
        next_state = next(states, None)

        if not state:
            raise NotImplementedError(state_code)

        if state.command:
            command = pydoc.locate(state.command)

            media = Media.objects.get(pk=media_id)

            command(media)

            media.processing_state_code = state.code
            media.save()

        if next_state and next_state.task:
            task = pydoc.locate(next_state.task)
            task.delay(media_id)
