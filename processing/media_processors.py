import inspect
import json

from channels import Group

from processing.processor import DataProcessor
from storage.const import MediaConstMixin


def is_image(media_type=None):
    return media_type == MediaConstMixin.MEDIA_IMAGE


def is_video(media_type=None):
    return media_type == MediaConstMixin.MEDIA_VIDEO


def is_other(media_type=None):
    return media_type == MediaConstMixin.MEDIA_OTHER


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

    # Save only those values that changed. For mutable objects (e.g. dict) we must receive a copy here.
    data = {k: v for k, v in kwargs.items() if v is not initial_state.get(k)}

    media = Media.objects.filter(id=media_id).only('id').get()

    for k, v in data.items():
        setattr(media, k, v)

    media.save(update_fields=data.keys())

    return 'media', media


def ws_notify_about_thumbnail(media=None):
    Group(f'upload-{media.uploader_id}').send({'text': json.dumps(
        ('thumbnail', {
            'media': {
                'id': media.id,
                'thumbnail': media.thumbnail.url if media.thumbnail else None
            }
        })
    )})
