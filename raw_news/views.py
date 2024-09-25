from django.http import HttpResponse
from django.shortcuts import redirect, render
import datetime
from django.views import View
import requests
from newsstats import settings
from raw_news.models import NewsDomain, NewsImage, ProcessedNews, RawNews
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import boto3
import os

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)


def dashboard_view(request):
    current_date = timezone.now().date()
    domains = NewsDomain.objects.all()
    total_news = RawNews.objects.all().count()
    total_p_news = ProcessedNews.objects.all().count()
    domain_data = []
    for domain in domains:
        total_raw_news = RawNews.objects.filter(domain_id=domain.id).count()
        todays_raw_news = RawNews.objects.filter(
            Q(domain_id=domain.id) &
            Q(created_at__date=current_date)
        ).count()
        total_processed_news = ProcessedNews.objects.filter(url__icontains=domain.domain_name).count()
        todays_processed_news = ProcessedNews.objects.filter(
            Q(url__icontains=domain.domain_name) &
            Q(processed_timestamp__date=current_date)
        ).count()
        domain_data.append({
            'domain_id': domain.id,
            'domain_name': domain.domain_name,
            'total_raw_news': total_raw_news,
            'todays_raw_news': todays_raw_news,
            'total_processed_news': total_processed_news,
            'todays_processed_news': todays_processed_news
        })

    paginator = Paginator(domain_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'raw_news/dashboard.html', {'domain_data': page_obj, 'total_news': total_news,
                                                       'total_p_news': total_p_news, })


def listing_view(request, id):
    try:
        domain = NewsDomain.objects.get(pk=id)
        domain_name = domain.domain_name
        listing_data = RawNews.objects.filter(domain_id=id)
        paginator = Paginator(listing_data, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'raw_news/listing.html', {'listing_data': page_obj, 'domain_name': domain_name})
    except NewsDomain.DoesNotExist:
        return render(request, "raw_news/error_page.html", {
            'exception': 'Domain listing not available!'
        })


class News_Update(View):
    def get(self, request, id):
        try:
            news = RawNews.objects.get(pk=id)
            return render(request, "raw_news/detailpage.html", {
                'news': news
            })
        except RawNews.DoesNotExist:
            return render(request, "raw_news/error_page.html", {
                'exception': 'News Not Available'
            })

    def post(self, request, id):
        try:
            raw_news = RawNews.objects.get(pk=id)
            changed_fields = []
            if raw_news.title != request.POST.get('title'):
                raw_news.title = request.POST.get('title')
                changed_fields.append('title')

            if raw_news.news_body != request.POST.get('news_body'):
                raw_news.news_body = request.POST.get('news_body')
                changed_fields.append('news_body')

            if raw_news.source != request.POST.get('source'):
                raw_news.source = request.POST.get('source')
                changed_fields.append('source')

            if raw_news.video_urls != request.POST.get('video_urls'):
                raw_news.video_urls = request.POST.get('video_urls')
                changed_fields.append('video_urls')

            if raw_news.is_advertisement != bool(request.POST.get('is_advertisement')):
                raw_news.is_advertisement = bool(request.POST.get('is_advertisement'))
                changed_fields.append('is_advertisement')

            if raw_news.target_area != request.POST.get('target_area'):
                raw_news.target_area = request.POST.get('target_area')
                changed_fields.append('target_area')

            if raw_news.target_gender != request.POST.get('target_gender'):
                raw_news.target_gender = request.POST.get('target_gender')
                changed_fields.append('target_gender')

            if raw_news.target_age_range != request.POST.get('target_age_range'):
                raw_news.target_age_range = request.POST.get('target_age_range')
                changed_fields.append('target_age_range')

            if raw_news.target_interests != request.POST.get('target_interests'):
                raw_news.target_interests = request.POST.get('target_interests')
                changed_fields.append('target_interests')
            raw_news.processed = 2
            changed_fields.append('processed')

            # Process image uploads
            image_urls_text = request.POST.get('image_urls')
            images = request.FILES.getlist('images')
            bucket_name = settings.AWS_S3_BUCKET
            for image in images:
                try:
                    image_name = f"news_images/{raw_news.id}/{image.name}"
                    s3_client.upload_fileobj(
                        image.file,
                        bucket_name,
                        image_name,
                        ExtraArgs={
                            'ContentType': image.content_type
                        }
                    )
                    # Construct the S3 URL
                    image_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{image_name}"
                    NewsImage.objects.create(
                        url=image_url,
                        image_id=raw_news
                    )
                except Exception as e:
                    return render(request, "raw_news/error_page.html", {
                        'exception': f'Image not uploaded: {e}'
                    })

            #Proces image urls
            if image_urls_text:
                image_urls = [url.strip() for url in image_urls_text.split(',') if url.strip()]
                for image_url in image_urls:
                    try:
                        response = requests.get(image_url, stream=True)
                        response.raise_for_status()
                        image_filered_name = f"{raw_news.id}/{image_url.split('.')[0]}"
                        if '/' in image_url:
                            image_extension = f"{raw_news.id}/{image_url.split('/')[-1]}"
                            if '.' in image_extension:
                                image_filered_name = image_extension.split('.')[0]

                        image_name = f"news_images/{image_filered_name}"
                        s3_client.upload_fileobj(
                            response.raw,
                            bucket_name,
                            image_name,
                            ExtraArgs={'ContentType': response.headers.get('Content-Type')}
                        )
                        uploaded_image_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{image_name}"
                        print(f'Uploaded image url: {uploaded_image_url}')
                        NewsImage.objects.create(
                            url=uploaded_image_url,
                            image_id=raw_news
                        )
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading image from URL: {image_url} - {e}")

            if changed_fields:
                raw_news.save(update_fields=changed_fields)

            return redirect('dashboard')
        except RawNews.DoesNotExist:
            return render(request, "raw_news/error_page.html", {
                'exception': 'News Not Available'
            })
        except Exception as e:
            return render(request, "raw_news/error_page.html", {
                'exception': f'Error: {e}'
            })
