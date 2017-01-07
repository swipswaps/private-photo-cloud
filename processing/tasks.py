from celery import shared_task


@shared_task
def initial_state(media_id):
    from processing import states
    states.InitialState.run(media_id)

@shared_task
def extract_base_metadata(media_id):
    from processing import states
    states.ExtractBaseMetadataState.run(media_id)


@shared_task
def generate_quick_thumbnail(media_id):
    from processing import states
    states.GenerateQuickThumbnailState.run(media_id)


@shared_task
def generate_play(media_id):
    from processing import states
    states.GeneratePlayState.run(media_id)


@shared_task
def calculate_metadata(media_id):
    from processing import states
    states.CalculateMetadataState.run(media_id)


@shared_task
def categorize(media_id):
    from processing import states
    states.CategorizeState.run(media_id)
