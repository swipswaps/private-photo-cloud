import logging
import datetime

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.template.response import TemplateResponse
from django.http import JsonResponse

from storage import models


logger = logging.getLogger(__name__)

@login_required
def upload(request):
    import uuid

    return TemplateResponse(request, 'upload.html', {
        'UPLOAD_SESSION_ID': uuid.uuid4().hex,
    })


@login_required
def upload_file(request):
    from storage.states import MediaState

    data = request.POST

    pk = {
        'uploader_id': request.user.id,
        'sha1_b85': models.Media.hex_to_base85(data['sha1']),
        'size_bytes': int(data['size'], 10)
    }

    media = models.Media(
        session_id=data['session_id'],
        source_filename=data['name'],
        mimetype=data['type'],
        # last_modified = microseconds since epoch
        source_lastmodified=datetime.datetime.fromtimestamp(int(data['last_modified'], 10) / 1000,
                                                            datetime.timezone.utc),
        content=request.FILES['file'],
        **pk
    )

    try:
        media.save()
    except MediaState.InvalidUploadError as ex:
        resp = JsonResponse({
            'error': f'Invalid upload: {ex.args[0]}'
        })
        resp.status_code = 400  # HTTP 400 Bad request
        return resp
    except IntegrityError:
        logger.warning(f'Uploaded duplicate image: {pk}')
        media = models.Media.objects.get(**pk)

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
