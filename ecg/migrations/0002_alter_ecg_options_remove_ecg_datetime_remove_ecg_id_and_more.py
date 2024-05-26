# Generated by Django 4.1.13 on 2024-05-11 16:21

from django.db import migrations
import django.utils.timezone
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ecg', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ecg',
            options={},
        ),
        migrations.RemoveField(
            model_name='ecg',
            name='dateTime',
        ),
        migrations.RemoveField(
            model_name='ecg',
            name='id',
        ),
        migrations.AddField(
            model_name='ecg',
            name='_id',
            field=djongo.models.fields.ObjectIdField(auto_created=True, default=django.utils.timezone.now, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]