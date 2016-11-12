# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-12 13:32
from __future__ import unicode_literals

from django.conf import settings
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
                ('media_type', models.IntegerField(choices=[(1, 'Photo'), (2, 'Video'), (3, 'Other')])),
                ('width', models.IntegerField(blank=True, help_text='Width for use', null=True)),
                ('height', models.IntegerField(blank=True, help_text='Height for use', null=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('content', models.FileField(upload_to=storage.models.Media.generate_content_filename)),
                ('size_bytes', models.BigIntegerField()),
                ('content_width', models.IntegerField(blank=True, help_text='Content width, before rotation', null=True)),
                ('content_height', models.IntegerField(blank=True, help_text='Content height, before rotation', null=True)),
                ('needed_rotate_degree', models.IntegerField(blank=True, help_text='How much content data need to be rotated to get correct orientation', null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('processing_state_code', models.IntegerField(default=0)),
                ('mimetype', models.CharField(max_length=127)),
                ('workflow_type', models.IntegerField(blank=True, choices=[(1, 'Raw'), (2, 'Original'), (3, 'Processed')], null=True)),
                ('source_filename', models.CharField(blank=True, max_length=255)),
                ('source_type', models.CharField(blank=True, max_length=63)),
                ('source_lastmodified', models.DateTimeField(null=True)),
                ('sha1_b85', models.CharField(db_index=True, max_length=25)),
                ('screenshot', models.ImageField(blank=True, height_field='height', help_text='Image taken from the video, sized 1:1 to rotated video', upload_to=storage.models.Media.generate_screenshot_filename, width_field='width')),
                ('thumbnail', models.ImageField(blank=True, height_field='thumbnail_height', upload_to=storage.models.Media.generate_thumbnail_filename, width_field='thumbnail_width')),
                ('thumbnail_width', models.IntegerField(blank=True, null=True)),
                ('thumbnail_height', models.IntegerField(blank=True, null=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
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
                ('shoot_at', models.DateTimeField()),
                ('device', models.CharField(blank=True, max_length=255)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('duration_seconds', models.IntegerField(blank=True, null=True)),
                ('thumbnail', models.ImageField(blank=True, height_field='thumbnail_height', upload_to='', width_field='thumbnail_width')),
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
        migrations.AddField(
            model_name='media',
            name='shot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.Shot'),
        ),
        migrations.AddField(
            model_name='media',
            name='uploader',
            field=models.ForeignKey(help_text='User that uploaded the media. He owns it.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='media',
            unique_together=set([('uploader', 'sha1_b85')]),
        ),
    ]
