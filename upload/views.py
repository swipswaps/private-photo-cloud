import logging
import datetime

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.template.response import TemplateResponse
from django.http import JsonResponse

from storage import models
from upload.forms import UploadForm

logger = logging.getLogger(__name__)


@login_required
def upload(request):
    import uuid

    return TemplateResponse(request, 'upload.html', {
        'UPLOAD_SESSION_ID': uuid.uuid4().hex,
    })


@login_required
def upload_file(request):
    form = UploadForm(request.POST, request.FILES)

    if not form.is_valid():
        resp = JsonResponse({
            'error': dict(form.errors)
        })
        print(form.errors)
        resp.status_code = 400  # HTTP 400 Bad request
        return resp

    media = models.Media(uploader_id=request.user.id, **form.model_data)

    try:
        # This save is as dummy as possible -- return only ID and do all processing in background
        media.save()
    except IntegrityError:
        logger.warning(f'Got duplicate image: {media.unique_key}')
        media = models.Media.objects.get(**media.unique_key)

    resp = JsonResponse({
        'media': {
            'id': media.id,
            'thumbnail': media.thumbnail.url if media.thumbnail else None,
        }
    })
    resp.status_code = 201  # HTTP 201 Created
    return resp


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
        return JsonResponse({'media': None})

    return JsonResponse({'media': {
        'id': media.id,
        'thumbnail': media.thumbnail.url if media.thumbnail else None,
    }})
