# -*- coding: utf-8 -*-
# Generated by Django 1.11a1 on 2017-01-22 20:54
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import storage.const
import storage.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField()),
                ('media_type', models.IntegerField(choices=[(1, 'Image'), (2, 'Video'), (3, 'Other')], null=True)),
                ('shot_at', models.DateTimeField(null=True)),
                ('show_at', models.DateTimeField(null=True)),
                ('width', models.IntegerField(blank=True, help_text='Width for use', null=True)),
                ('height', models.IntegerField(blank=True, help_text='Height for use', null=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('content', models.FileField(upload_to=storage.models.Media.generate_content_filename)),
                ('size_bytes', models.BigIntegerField()),
                ('needed_rotate_degree', models.IntegerField(blank=True, help_text='How much content data need to be rotated to get correct orientation', null=True)),
                ('categories', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, default=list, size=None)),
                ('processing_state_code', models.IntegerField(default=0)),
                ('mimetype', models.CharField(max_length=127)),
                ('source_filename', models.CharField(blank=True, max_length=255)),
                ('source_lastmodified', models.DateTimeField(null=True)),
                ('sha1_b85', models.CharField(db_index=True, max_length=25)),
                ('screenshot', models.FileField(blank=True, help_text='Image taken from the video, sized 1:1 to rotated video', upload_to=storage.models.Media.generate_screenshot_filename)),
                ('thumbnail', models.FileField(blank=True, upload_to=storage.models.Media.generate_thumbnail_filename)),
                ('thumbnail_width', models.IntegerField(blank=True, null=True)),
                ('thumbnail_height', models.IntegerField(blank=True, null=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('shot_id', models.IntegerField(blank=True, null=True)),
                ('camera', models.CharField(blank=True, max_length=255)),
                ('uploader', models.ForeignKey(help_text='User that uploaded the media. He owns it.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(storage.const.MediaConstMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Shot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.IntegerField(choices=[(1, 'Photo'), (2, 'Video')])),
                ('orientation', models.IntegerField(choices=[(1, 'Landscape'), (2, 'Portrait'), (3, 'Square')])),
                ('aspect_ratio', models.IntegerField(choices=[(1, '16:9'), (2, '4:3'), (3, '1:1'), (0, 'Other')])),
                ('shot_at', models.DateTimeField()),
                ('device', models.CharField(blank=True, max_length=255)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('duration_seconds', models.IntegerField(blank=True, null=True)),
                ('thumbnail', models.FileField(blank=True, upload_to='')),
                ('thumbnail_width', models.IntegerField(blank=True, null=True)),
                ('thumbnail_height', models.IntegerField(blank=True, null=True)),
                ('uploader', models.ForeignKey(help_text='User that uploaded the media. He owns it.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(storage.const.ShotConstMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ShotCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='media',
            unique_together=set([('uploader', 'sha1_b85', 'size_bytes')]),
        ),
    ]
