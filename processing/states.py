import pydoc
from collections import namedtuple
from itertools import zip_longest

State = namedtuple('State', ['code', 'task', 'command'])


class ProcessingState:
    # Use sparse codes to have chance to put anything between
    STATE_INITIAL = 0
    STATE_BASE_METADATA = 5
    STATE_QUICK_THUMBNAIL = 10
    STATE_PLAY_MEDIA = 15
    STATE_METADATA = 20
    STATE_CATEGORIES = 25
    STATE_GROUPS = 30

    STATES = (
        State(STATE_INITIAL, 'processing.tasks.initial_state', None),
        State(STATE_BASE_METADATA, 'processing.tasks.extract_base_metadata', 'processing.base_metadata.run'),
        State(STATE_QUICK_THUMBNAIL, 'processing.tasks.generate_quick_thumbnail', 'processing.quick_thumbnail.run'),
        State(STATE_PLAY_MEDIA, 'processing.tasks.generate_play', 'processing.play_media.run'),
        State(STATE_METADATA, 'processing.tasks.calculate_metadata', 'processing.metadata.run'),
        State(STATE_CATEGORIES, 'processing.tasks.categorize', 'processing.categories.run'),
        State(STATE_GROUPS, 'processing.tasks.group', 'processing.groups.run'),
    )

    STATES_DICT = {state.code: (state, next_state)
                   for state, next_state in zip_longest(STATES, STATES[1:])}

    @classmethod
    def run(cls, state_code, media_id):
        from storage.models import Media

        state, next_state = cls.STATES_DICT.get(state_code, (None, None))

        if not state:
            raise NotImplementedError(state_code)

        if state.command:
            command = pydoc.locate(state.command)
            try:
                command(media_id=media_id)
                Media.objects.filter(id=media_id).update(processing_state_code=state.code)
            except Exception:
                # TODO: Ensure we commit changes here despite of exception later
                Media.objects.filter(id=media_id).update(processing_state_code=-state.code)
                raise

        if next_state and next_state.task:
            task = pydoc.locate(next_state.task)
            task.delay(media_id)
