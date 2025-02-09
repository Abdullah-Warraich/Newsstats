# Generated by Django 5.1 on 2024-09-19 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RawNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_name', models.CharField(max_length=500)),
                ('url', models.CharField(max_length=500)),
                ('title', models.CharField(max_length=500)),
                ('news_body', models.TextField()),
                ('source', models.CharField(max_length=500)),
                ('published_at', models.DateTimeField()),
                ('processed', models.BooleanField(default=False)),
                ('video_urls', models.TextField(blank=True)),
                ('is_advertisement', models.BooleanField(default=False)),
                ('target_area', models.CharField(blank=True, max_length=500)),
                ('target_gender', models.CharField(blank=True, max_length=500)),
                ('target_age_range', models.CharField(blank=True, max_length=500)),
                ('target_interests', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'news_table',
            },
        ),
    ]
