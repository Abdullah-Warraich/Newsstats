from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.db import models
from django.core.validators import URLValidator

class RawNews(models.Model):
    domain_id = models.IntegerField(null=True)
    url = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    news_body = models.TextField()
    source = models.CharField(max_length=500)
    published_at = models.DateTimeField()
    processed = models.IntegerField(default=0)
    video_urls = models.TextField(blank=True)
    is_advertisement = models.BooleanField(default=False)
    target_area = models.CharField(max_length=500, blank=True)
    target_gender = models.CharField(max_length=500, blank=True)
    target_age_range = models.CharField(max_length=500, blank=True)
    target_interests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_table'


class NewsDomain(models.Model):
    domain_name = models.TextField(blank=True)


    class Meta:
        db_table = 'news_domain_table'
    
class ProcessedNews(models.Model):
    news_id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=500)
    processed_timestamp = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'processed_news_table'


class NewsImage(models.Model):
    url = models.TextField()
    image_id = models.ForeignKey(RawNews, on_delete=models.CASCADE, related_name="image_id", db_column="image_id")

    class Meta:
        db_table = 'news_images_table'

