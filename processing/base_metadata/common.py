import inspect
import os

from django.db.models.fields.files import FieldFile

from processing.base_metadata import DataProcessor
from storage.const import MediaConstMixin
from storage.helpers import get_first_filled_value, base85_to_hex

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

    # Save only those values that changed. For mutable objects (e.g. dict) we must receive a copy here.
    data = {k: v for k, v in kwargs.items() if v is not initial_state.get(k)}

    media = Media.objects.filter(id=media_id).only('id').get()

    for k, v in data.items():
        setattr(media, k, v)

    media.save(update_fields=data.keys())

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

    # Alternative: exiv2 (faster but less formats)
    # See: http://dev.exiv2.org/projects/exiv2/wiki/How_does_Exiv2_compare_to_Exiftool

    # Create a clone before update -- to keep initial state immutable
    return 'metadata', dict(metadata or {}, exiftool=get_exiftool_info(content.path))


def MimetypeByExiftoolMetadata(media_type=None, metadata=None):
    if media_type not in VISUAL_TYPES:
        return

    mimetype = metadata['exiftool'].get('File:MIMEType')

    if mimetype:
        # Do not overwrite if empty
        return 'mimetype', mimetype


class ContentByExtensionShowAt:
    EXTENSION_BY_MIME = {
        # value MUST start with ".", e.g. ".jpg"
        'image/x-canon-cr2': '.cr2',
        'image/x-nikon-nef': '.nef',
        'image/jpeg': '.jpg',
    }

    @staticmethod
    def run(mimetype=None, source_filename=None, content=None, uploader_id=None, show_at=None, sha1_b85=None,
            size_bytes=None):
        from storage.models import Media

        content_name = Media.generate_content_filename_permanent(
            uploader_id=uploader_id,
            show_at=show_at,
            sha1_hex=base85_to_hex(sha1_b85),
            size_bytes=size_bytes,
            content_extension=get_first_filled_value(
                ContentByExtensionShowAt.get_content_extension(mimetype=mimetype, source_filename=source_filename)
            )
        )

        if content_name == content.name:
            return

        # NOTE: This changes file system state => make it as late as possible, right before `Media.save`
        Media.move_file(storage=content.storage, old_path=content.name, new_path=content_name)

        return 'content', FieldFile(instance=content.instance, field=content.field, name=content_name)

    @staticmethod
    def get_content_extension(mimetype=None, source_filename=None):
        import mimetypes

        yield ContentByExtensionShowAt.EXTENSION_BY_MIME.get(mimetype)
        yield mimetypes.guess_extension(mimetype)

        # Fallback to source file extension
        yield os.path.splitext(source_filename)[1].lower()
