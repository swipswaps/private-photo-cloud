from rest_framework import serializers

from storage.models import Media


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        exclude = (
            'sha1_b85',
            'session_id',
            'uploader',
        )


class MSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = (
            'id',
            # TODO: Re-implement the logic of upload.views.uploaded_media2dict
            'thumbnail',
        )