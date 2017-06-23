import datetime
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter

from catalog.rest_serializers import MediaSerializer, MSerializer
from storage.models import Media


class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method and request.method in permissions.SAFE_METHODS


class MediaFilter(FilterSet):
    show_year = NumberFilter(name="show_at", lookup_expr="year", min_value=datetime.MINYEAR, max_value=datetime.MAXYEAR)
    show_month = NumberFilter(name="show_at", lookup_expr="month", min_value=1, max_value=12)

    class Meta:
        model = Media
        fields = ('show_year', 'show_month')


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ReadOnlyPermission,
    )
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filter_class = MediaFilter
    ordering_fields = ('show_at',)
    ordering = ('show_at',)

    def get_queryset(self):
        return super().get_queryset().filter(uploader=self.request.user)

class MViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ReadOnlyPermission,
    )

    def get_queryset(self):
        return super().get_queryset().filter(uploader=self.request.user)
