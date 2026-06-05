# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'estoque_initial_data.json')


def unload_fixture(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('estoque', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_fixture, unload_fixture),
    ]
