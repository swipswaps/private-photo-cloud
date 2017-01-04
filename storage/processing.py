import logging
from celery import shared_task, Task

logger = logging.getLogger(__name__)


def extract_base_metadata(media):
    logger.info('extract base metadata')


def generate_quick_thumbnail(media):
    logger.info('generate quick thumbnail')


def generate_play(media):
    logger.info('generate play')
    # TODO: Mark media as ready for "play"


def calculate_metadata(media):
    logger.info('calculate metadata')


def categorize(media):
    logger.info('categorize')


def process_state(state_code, media_id, fn):
    from storage.models import Media
    media = Media.objects.get(pk=media_id)

    fn(media)

    media.processing_state_code = state_code
    media.save()


@shared_task
def media_initial(media_id):
    media_extract_base_metadata.delay(media_id)


@shared_task
def media_extract_base_metadata(media_id):
    process_state(1, media_id, extract_base_metadata)
    media_generate_quick_thumbnail.delay(media_id)


@shared_task
def media_generate_quick_thumbnail(media_id):
    process_state(2, media_id, generate_quick_thumbnail)
    media_generate_play.delay(media_id)


@shared_task
def media_generate_play(media_id):
    process_state(3, media_id, generate_play)
    media_calculate_metadata.delay(media_id)


@shared_task
def media_calculate_metadata(media_id):
    process_state(4, media_id, calculate_metadata)
    media_categorize.delay(media_id)


@shared_task
def media_categorize(media_id):
    process_state(5, media_id, categorize)
