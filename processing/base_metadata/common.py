import inspect

from processing.base_metadata import DataProcessor
from storage.const import MediaConstMixin

TYPES = {
    'image': MediaConstMixin.MEDIA_IMAGE,
    'video': MediaConstMixin.MEDIA_VIDEO,
}
TYPE_DEFAULT = MediaConstMixin.MEDIA_OTHER
VISUAL_TYPES = (MediaConstMixin.MEDIA_IMAGE, MediaConstMixin.MEDIA_VIDEO)


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
    data = {k: v for k, v in kwargs.items() if v is not initial_state.get(k)}

    media = Media.objects.filter(id=media_id).only('id').get()

    for k, v in data.items():
        setattr(media, k, v)

    media.save(update_fields=data)

    return 'media', media



def MimetypeByContent(content=None):
    import magic

    return 'mimetype', magic.from_file(content.path, mime=True)


def MediatypeByMimeType(mimetype=None):
    return 'media_type', TYPES.get(mimetype.split('/')[0], TYPE_DEFAULT)


def ShowAtByShotAtSourceLastModified(shot_at=None, source_lastmodified=None):
    if shot_at:
        return 'show_at', shot_at
    return 'show_at', source_lastmodified


def ExiftoolMetadataByContent(content=None, media_type=None, metadata=None):
    from storage.tools.exiftool import get_exiftool_info

    if media_type not in VISUAL_TYPES:
        return

    metadata = metadata or {}

    # Alternative: exiv2 (faster but less formats)
    # See: http://dev.exiv2.org/projects/exiv2/wiki/How_does_Exiv2_compare_to_Exiftool
    metadata['exiftool'] = get_exiftool_info(content.path)

    return 'metadata', metadata


def MimetypeByExiftoolMetadata(media_type=None, metadata=None):
    if media_type not in VISUAL_TYPES:
        return

    mimetype = metadata['exiftool'].get('File:MIMEType')

    if mimetype:
        # Do not overwrite if empty
        return 'mimetype', mimetype
