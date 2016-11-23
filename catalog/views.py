from django.template.response import TemplateResponse


def catalog(request):
    return TemplateResponse(request, "catalog.html")