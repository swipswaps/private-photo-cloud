from celery import shared_task

from processing.states import ProcessingState


@shared_task
def initial_state(media_id):
    ProcessingState.run(state_code=ProcessingState.STATE_INITIAL, media_id=media_id)


@shared_task
def extract_base_metadata(media_id):
    ProcessingState.run(state_code=ProcessingState.STATE_BASE_METADATA, media_id=media_id)


@shared_task
def generate_quick_thumbnail(media_id):
    ProcessingState.run(state_code=ProcessingState.STATE_QUICK_THUMBNAIL, media_id=media_id)


@shared_task
def generate_play(media_id):
    ProcessingState.run(state_code=ProcessingState.STATE_PLAY_MEDIA, media_id=media_id)


@shared_task
def calculate_metadata(media_id):
    ProcessingState.run(state_code=ProcessingState.STATE_METADATA, media_id=media_id)


@shared_task
def categorize(media_id):
    ProcessingState.run(state_code=ProcessingState.STATE_CATEGORIES, media_id=media_id)


@shared_task
def group(media_id):
    ProcessingState.run(state_code=ProcessingState.STATE_GROUPS, media_id=media_id)
