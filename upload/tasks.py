from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def run_group_media_into_shot(session_id, media_id):
    from classification.group_media_into_shot import process
    process(session_id=session_id, media_id=media_id)
