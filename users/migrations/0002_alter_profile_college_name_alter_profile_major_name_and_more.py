# Generated by Django 4.0.2 on 2022-02-09 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='college_name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='profile',
            name='major_name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='profile',
            name='mbti',
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AlterField(
            model_name='profile',
            name='university_name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterModelTable(
            name='profile',
            table='profile',
        ),
    ]