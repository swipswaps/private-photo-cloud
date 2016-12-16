import logging
import datetime

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.template.response import TemplateResponse
from django.http import JsonResponse, HttpResponseNotFound

from storage import models
from upload.forms import UploadForm

logger = logging.getLogger(__name__)


@login_required
def upload(request):
    import uuid

    return TemplateResponse(request, 'upload.html', {
        'UPLOAD_SESSION_ID': uuid.uuid4().hex,
    })


def uploaded_media2dict(media):
    return {'media':
        {
            'id': media.id,
            # Exclamation mark would indicate that there is no thumbnail yet
            'thumbnail': media.thumbnail.url if media.thumbnail else '!',
        }
    }


@login_required
def upload_file(request):
    form = UploadForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse({'error': dict(form.errors)}, status=400)   # HTTP 400 Bad request

    media = models.Media(uploader_id=request.user.id, **form.model_data)

    try:
        # This save is as dummy as possible -- return only ID and do all processing in background
        media.save()
        return JsonResponse(uploaded_media2dict(media), status=201) # HTTP 201 Created

    except IntegrityError:
        logger.warning(f'Got duplicate image: {media.unique_key}')
        media = models.Media.objects.get(**media.unique_key)
        return JsonResponse(uploaded_media2dict(media))


@login_required
def check_present(request, alg=None, digest=None, size=None):
    import binascii
    import base64

    if alg == 'sha1':
        digest_b85 = base64.b85encode(binascii.unhexlify(digest))
    else:
        raise NotImplemented(f'Unknown algorithm {alg}')

    try:
        media = models.Media.objects.get(uploader=request.user, sha1_b85=digest_b85, size_bytes=size)
    except models.Media.DoesNotExist:
        return HttpResponseNotFound()

    return JsonResponse(uploaded_media2dict(media))
