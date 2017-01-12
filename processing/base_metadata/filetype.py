from storage.const import MediaConstMixin

TYPES = {
    'image': MediaConstMixin.MEDIA_IMAGE,
    'video': MediaConstMixin.MEDIA_VIDEO,
}
TYPE_DEFAULT = MediaConstMixin.MEDIA_OTHER


def MimetypeByContent(content=None):
    import magic

    return 'mimetype', magic.from_file(content.path, mime=True)


def MediatypeByMimeType(mimetype=None):
    return 'media_type', TYPES.get(mimetype.split('/')[0], TYPE_DEFAULT)
