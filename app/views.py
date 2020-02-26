from django.conf import settings
from django.shortcuts import render

from app.models import TempData
from app.services import stat_service, vk_api_service


def index(request):
    host = 'http://192.168.1.100:8080/' if settings.DEBUG else '/'

    result = {
        'google_analytics_id': '',
        'js_files': [
            f'{host}js/app.js',
            f'{host}js/chunk-vendors.js'
        ],
        'css_files': [],
        'frontendData': {
            'user': {
                'username': request.user.username,
                'is_superuser': 1 if request.user.is_superuser else 0
            },
            'stat': stat_service.get_stat(),
            'lastSyncDate': TempData.objects.get().last_sync_date.timestamp(),
            'config': {
                'projectVersion': settings.VERSION,
                'groupLink': vk_api_service.get_group_url()
            }
        }
    }
    return render(request, 'app/index.html', result)
