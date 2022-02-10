# Generated by Django 4.0.2 on 2022-02-10 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room_type', models.IntegerField(max_length=1)),
                ('title', models.CharField(max_length=64)),
                ('grade_limit', models.IntegerField(max_length=1, null=True)),
                ('heads_limit', models.IntegerField(max_length=1)),
                ('gender_limit', models.IntegerField(max_length=1, null=True)),
                ('meet_purpose', models.CharField(blank=True, max_length=255)),
                ('room_description', models.CharField(blank=True, max_length=255)),
                ('meet_status', models.CharField(blank=True, max_length=1)),
                ('room_open', models.CharField(default='Y', max_length=1)),
                ('common', models.TextField(blank=True)),
                ('mbti', models.CharField(blank=True, max_length=4)),
                ('interest', models.TextField(blank=True)),
                ('college', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'rooms',
            },
        ),
        migrations.CreateModel(
            name='RoomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'room_users',
            },
        ),
        migrations.AddField(
            model_name='room',
            name='owner',
            field=models.ManyToManyField(through='users.RoomUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('university_name', models.CharField(max_length=32)),
                ('college_name', models.CharField(max_length=32)),
                ('major_name', models.CharField(max_length=32)),
                ('school_email', models.EmailField(max_length=254)),
                ('birth_of_date', models.DateField(null=True)),
                ('gender', models.IntegerField(null=True)),
                ('age', models.IntegerField(null=True)),
                ('entrance_year', models.IntegerField(null=True)),
                ('grade', models.IntegerField(null=True)),
                ('nickname', models.CharField(max_length=200)),
                ('introducing', models.CharField(blank=True, max_length=255)),
                ('school_auth_status', models.BooleanField(default=False)),
                ('registration_date', models.DateField(auto_now_add=True)),
                ('mbti', models.CharField(blank=True, max_length=4)),
                ('interest_list', models.TextField(blank=True)),
                ('withdrawn_status', models.CharField(default='N', max_length=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'profile',
            },
        ),
    ]
