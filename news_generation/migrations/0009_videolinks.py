# Generated by Django 4.2 on 2023-05-02 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news_generation', '0008_translatedarticles'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoLinks',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('v_id', models.CharField(max_length=255)),
                ('video_url', models.TextField(blank=True, default=None, null=True)),
                ('language', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='news_generation.languages')),
            ],
        ),
    ]
