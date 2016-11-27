from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.template.response import TemplateResponse

from storage.models import Media


@login_required
def catalog(request):
    return TemplateResponse(request, "catalog.html")


# date_trunc('{field}', {source})

@login_required
def images_months(request):
    qs = Media.objects.filter(uploader=request.user)
    # That gives only dates, no aggregation possible
    months = sorted(qs.dates('show_at', 'month'))
    return JsonResponse({"months": [m.strftime('%Y-%m') for m in months]})


MEDIA_FIELDS = (
    "id",
    "show_at",
    "shot_at",
    "thumbnail",
    "thumbnail_width",
    "thumbnail_height",
    "camera",
    "media_type",
    "size_bytes",
    "width",
    "height",
    "content",
    "screenshot",
    "mimetype",
    "source_filename",
)


@login_required
def images_for_month(request, year=None, month=None):
    qs = Media.objects.filter(uploader=request.user)

    qs = qs.filter(show_at__year=year, show_at__month=month)

    return JsonResponse({"media": list(qs.values(*MEDIA_FIELDS).order_by("show_at"))})
