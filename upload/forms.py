import datetime
import hashlib
import os

import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from storage.helpers import map_dict
from storage.tools.binhash import get_sha1_hex

RE_HEX = re.compile(r'^[0-9a-f]+$')


def validate_hex(value):
    if not RE_HEX.search(value):
        raise ValidationError(_('%(value)s is a hex string'),
                              code='invalid',
                              params={'value': value})


class UploadForm(forms.Form):
    session_id = forms.UUIDField()
    sha1 = forms.CharField(min_length=40, max_length=40, validators=[validate_hex])
    size = forms.IntegerField(min_value=0)
    last_modified = forms.IntegerField(min_value=0)
    name = forms.CharField(max_length=255)
    type = forms.CharField(max_length=127, required=False)
    file = forms.FileField()

    FIELDS_MAPPING = {
        'last_modified': 'source_lastmodified',
        'name': 'source_filename',
        'type': 'mimetype',
        'file': 'content',
        'size': 'size_bytes',
        'sha1': 'sha1_hex',
    }

    def clean_last_modified(self):
        # last_modified is microseconds since epoch
        return datetime.datetime.fromtimestamp(self.cleaned_data['last_modified'] / 1000, datetime.timezone.utc)

    def clean_name(self):
        return os.path.basename(self.cleaned_data['name'])

    def clean(self):
        cleaned_data = super().clean()

        uploaded_file = cleaned_data['file']

        try:
            # duck-typing
            uploaded_file_path = uploaded_file.temporary_file_path()
        except AttributeError:
            # File is in memory -- calculate SHA1 via Python
            actual_sha1 = hashlib.sha1(uploaded_file.read()).hexdigest()
        else:
            # File is in file system -- calculate SHA1 via binary tool
            actual_sha1 = get_sha1_hex(uploaded_file_path)

        if actual_sha1 != cleaned_data['sha1']:
            raise ValidationError({
                'file': _('File content does not match hash provided: {!r} != {!r}'.format(actual_sha1,
                                                                                           cleaned_data['sha1'])),
            })

        if uploaded_file.size != cleaned_data['size']:
            raise ValidationError({
                'file': _('File size does not match one provided: {!r} != {!r}'.format(uploaded_file.size,
                                                                                       cleaned_data['size'])),
            })

        return cleaned_data

    @property
    def model_data(self):
        return map_dict(self.cleaned_data, self.FIELDS_MAPPING)
