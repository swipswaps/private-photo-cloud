from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class Thumbnail:
    THUMBNAIL_RESIZE_SETTINGS = {
        'size': (160, 160),
        'resample': Image.LANCZOS,  # Image.NEAREST | Image.BILINEAR | Image.BICUBIC | Image.LANCZOS
    }

    THUMBNAIL_SETTINGS = {
        'format': 'JPEG',
        'quality': 95,
        'progressive': True,
        'optimize': True,
    }
    MIMETYPE = 'image/jpeg'

    class SourceImageError(ValueError):
        pass

    @staticmethod
    def generate_from_path(path=None, needed_rotate_degree=None, name='thumbnail.jpg'):
        # TODO: Refactor
        thumbnail_file = SimpleUploadedFile(name=name, content=b'', content_type=Thumbnail.MIMETYPE)

        with open(path, 'rb') as f:
            return Thumbnail.generate_from_fp(f=f, target=thumbnail_file, needed_rotate_degree=needed_rotate_degree)

    @staticmethod
    def generate_from_file(obj=None, needed_rotate_degree=None, name='thumbnail.jpg'):
        thumbnail_file = SimpleUploadedFile(name=name, content=b'', content_type=Thumbnail.MIMETYPE)

        return Thumbnail.generate_from_fp(f=obj, target=thumbnail_file, needed_rotate_degree=needed_rotate_degree)

    @staticmethod
    def generate_from_fp(f, target, needed_rotate_degree):
        try:
            image = Image.open(f)
        except OSError as ex:
            raise Thumbnail.SourceImageError(*ex.args)

        size = None, None

        try:
            image.thumbnail(**Thumbnail.THUMBNAIL_RESIZE_SETTINGS)
            # TODO: Sharpen by taste or multi-step downsampling

            # Rotate thumbnail, not whole image
            if needed_rotate_degree:
                # PIL rotate rotates counter clockwise => invert it
                thumbnail = image.rotate(-needed_rotate_degree, expand=True)
            else:
                thumbnail = image

            size = thumbnail.size
            thumbnail.save(target, **Thumbnail.THUMBNAIL_SETTINGS)
        finally:
            image.close()

        return {
            'thumbnail': target,
            'thumbnail_width': size[0],
            'thumbnail_height': size[1],
        }
