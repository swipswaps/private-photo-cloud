import tempfile

from processing.media_processors import is_image


def ThumbnailByContentDegree(media_type=None, content=None, needed_rotate_degree=None):
    from processing.quick_thumbnail.thumbnail import Thumbnail

    if not is_image(media_type):
        return

    try:
        return 'thumbnail', Thumbnail.generate_from_path(content.path, needed_rotate_degree=needed_rotate_degree)
    except Thumbnail.SourceImageError:
        return 'thumbnail', None


def ThumbnailByExiftoolMetadataEmbedContentDegree(media_type=None, thumbnail=None, metadata=None, content=None,
                                                  needed_rotate_degree=None):
    from storage.tools.exiftool import extract_any_embed_image
    from processing.quick_thumbnail.thumbnail import Thumbnail

    if not is_image(media_type):
        return

    if thumbnail:
        return

    with tempfile.TemporaryFile('w+b') as embed_image:
        # Use biggest image to generate thumbnail
        extract_any_embed_image(metadata['exiftool'], content.path, target=embed_image, biggest=True)

        return 'thumbnail', Thumbnail.generate_from_file(embed_image, needed_rotate_degree=needed_rotate_degree)
