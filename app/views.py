from django.conf import settings
from django.shortcuts import render
from rest_framework import viewsets, mixins

from app.models import TempData, Post
from app.serializers import PostSerializer
from app.services import stat_service, vk_api_service


def index(request):
    host = 'http://192.168.1.100:8080/' if settings.DEBUG else '/'

    user = request.user
    result = {
        'google_analytics_id': '',
        'js_files': [
            f'{host}js/app.js',
            f'{host}js/chunk-vendors.js'
        ],
        'css_files': [],
        'frontend_data': {
            'user': {
                'username': user.username,
                'isSuperuser': request.user.is_superuser
            } if user.is_authenticated else None,
            'stat': stat_service.get_stat(),
            'lastSyncDate': TempData.objects.get().last_sync_date.timestamp(),
            'config': {
                'projectVersion': settings.VERSION,
                'groupLink': vk_api_service.get_group_url()
            }
        }
    }
    return render(request, 'app/index.html', result)


class PostViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.order_by('-date')
    serializer_class = PostSerializer
