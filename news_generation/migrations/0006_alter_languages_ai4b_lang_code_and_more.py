# Generated by Django 4.2 on 2023-04-28 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_generation', '0005_languages_translatedarticles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='languages',
            name='ai4b_lang_code',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='languages',
            name='aks_lang_code',
            field=models.CharField(max_length=255, null=True),
        ),
    ]