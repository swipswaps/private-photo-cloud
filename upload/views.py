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
        source_type=data['type'],
        media_type_by_text=data['type'],
        source_lastmodified_time=int(data['last_modified'], 10) / 1000.0,
        sha1_hex=data['sha1'],
        content=request.FILES['file'],

        width=0,
        height=0,
        content_width=0,
        content_height=0,
        is_default=0,
        workflow_type=1,
    )
    # TODO: Re-calculate size and sha1
    media.save()

    resp = JsonResponse({'media': {'id': media.id}})
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
        media = {'id': models.Media.objects.get(uploader=request.user,
                                                sha1_b85=digest_b85).id}
    except models.Media.DoesNotExist:
        media = None

    return JsonResponse({'media': media})
