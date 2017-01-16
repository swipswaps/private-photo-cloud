import os

from django.db.models.fields.files import FieldFile

from processing.media_processors import is_image, is_video
from storage.const import MediaConstMixin
from storage.helpers import get_first_filled_value, base85_to_hex


def MimetypeByContent(content=None):
    import magic

    return 'mimetype', magic.from_file(content.path, mime=True)


class MediatypeByMimeType:
    TYPES = {
        'image': MediaConstMixin.MEDIA_IMAGE,
        'video': MediaConstMixin.MEDIA_VIDEO,
    }
    TYPE_DEFAULT = MediaConstMixin.MEDIA_OTHER

    @staticmethod
    def run(mimetype=None):
        return 'media_type', MediatypeByMimeType.TYPES.get(mimetype.split('/')[0], MediatypeByMimeType.TYPE_DEFAULT)


def ShowAtByShotAtSourceLastModified(shot_at=None, source_lastmodified=None):
    if shot_at:
        return 'show_at', shot_at
    return 'show_at', source_lastmodified


def ExiftoolMetadataByContent(content=None, media_type=None, metadata=None):
    from storage.tools.exiftool import get_exiftool_info

    if not is_image(media_type) and not is_video(media_type):
        return

    # Alternative: exiv2 (faster but less formats)
    # See: http://dev.exiv2.org/projects/exiv2/wiki/How_does_Exiv2_compare_to_Exiftool

    # Create a clone before update -- to keep initial state immutable
    return 'metadata', dict(metadata or {}, exiftool=get_exiftool_info(content.path))


def MimetypeByExiftoolMetadata(media_type=None, metadata=None):
    if not is_image(media_type) and not is_video(media_type):
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

        content_field = Media._meta.get_field('content')

        # NOTE: This changes file system state => make it as late as possible, right before `Media.save`
        Media.move_file(storage=content_field.storage, old_name=content.name, new_name=content_name)

        return 'content', FieldFile(instance=None, field=content_field, name=content_name)

    @staticmethod
    def get_content_extension(mimetype=None, source_filename=None):
        import mimetypes

        yield ContentByExtensionShowAt.EXTENSION_BY_MIME.get(mimetype)
        yield mimetypes.guess_extension(mimetype)

        # Fallback to source file extension
        yield os.path.splitext(source_filename)[1].lower()
