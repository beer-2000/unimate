# Generated by Django 4.0.2 on 2022-02-18 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_phone_auth'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='university',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
