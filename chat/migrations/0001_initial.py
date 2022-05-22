# Generated by Django 4.0.2 on 2022-05-22 06:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='timestamp')),
                ('body', models.TextField(verbose_name='body')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_room', to='rooms.room', verbose_name='room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]
