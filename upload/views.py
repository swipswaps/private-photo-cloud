from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse


@login_required
def upload(request):
    import uuid

    return TemplateResponse(request, 'upload.html', {
        'UPLOAD_SESSION_ID': uuid.uuid4().hex,
    })
