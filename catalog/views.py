from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.template.response import TemplateResponse

from storage.models import Media


@login_required
def catalog(request):
    return TemplateResponse(request, "catalog.html", {
        'categories': sorted(Media.categories_w_count(uploader=request.user)),
    })


# date_trunc('{field}', {source})

# TODO: Migrate to view in REST Framework
@login_required
def images_months(request):
    qs = Media.objects.filter(uploader=request.user)
    qs = qs.annotate(month=TruncMonth('show_at')).values_list('month').order_by('month').annotate(Count('id'))
    return JsonResponse({"months": [{'month': m.strftime('%Y-%m'), 'num': num} for m, num in qs]})


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
    "shot_id",
    "source_filename",
)


@login_required
def images_for_month(request, year=None, month=None):
    qs = Media.objects.filter(uploader=request.user)

    qs = qs.filter(show_at__year=year, show_at__month=month)

    # TODO: Use REST API /api/media/?show_year=year&show_month=month
    return JsonResponse({"media": list(qs.values(*MEDIA_FIELDS).order_by("show_at"))})
