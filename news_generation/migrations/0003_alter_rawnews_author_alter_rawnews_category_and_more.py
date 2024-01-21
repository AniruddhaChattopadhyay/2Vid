# Generated by Django 4.2 on 2023-04-27 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_generation', '0002_rawnews_image_url_rawnews_original_source_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawnews',
            name='author',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='rawnews',
            name='category',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='rawnews',
            name='original_source',
            field=models.TextField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='rawnews',
            name='source',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]