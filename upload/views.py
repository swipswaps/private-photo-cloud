import datetime
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.http import JsonResponse

from storage import models

@login_required
def upload(request):
    import uuid

    return TemplateResponse(request, 'upload.html', {
        'UPLOAD_SESSION_ID': uuid.uuid4().hex,
    })


@login_required
def upload_file(request):
    data = request.POST

    media = models.Media(
        uploader_id=request.user.id,
        session_id=data['session_id'],
        source_filename=data['name'],
        size_bytes=data['size'],
        mimetype=data['type'],
        # last_modified = microseconds since epoch
        source_lastmodified=datetime.datetime.fromtimestamp(int(data['last_modified'], 10) / 1000,
                                                            datetime.timezone.utc),
        sha1_hex=data['sha1'],
        content=request.FILES['file'],
    )
    # TODO: Re-calculate size and sha1
    media.save()

    resp = JsonResponse({'media': {
        'id': media.id,
        'thumbnail': media.thumbnail.url if media.thumbnail else None,
    }})
    resp.status_code = 201
    return resp


@login_required
def check_present(request, alg=None, digest=None):
    import binascii
    import base64

    if alg == 'sha1':
        digest_b85 = base64.b85encode(binascii.unhexlify(digest))
    else:
        raise NotImplemented(f'Unknown algorithm {alg}')

    try:
        media = models.Media.objects.get(uploader=request.user, sha1_b85=digest_b85)
    except models.Media.DoesNotExist:
        return JsonResponse({'media': None})

    return JsonResponse({'media': {
        'id': media.id,
        'thumbnail': media.thumbnail.url if media.thumbnail else None,
    }})
