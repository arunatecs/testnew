# Generated by Django 4.1.13 on 2024-05-13 13:57

from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('value', djongo.models.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Breathrate',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('value', djongo.models.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Ecg',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('value', djongo.models.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='HeartRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('dateTime', models.DateField()),
                ('value', djongo.models.fields.JSONField()),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
    ]