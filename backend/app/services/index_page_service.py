import os
from typing import List

from django.conf import settings
from django.templatetags.static import static

from app.models import TempData
from app.serializers import FrontendDataSerializer
from app.services import stat_service, vk_api_service
from app.util import encode_json, date_to_js_unix_time


def get_data(user):
    serializer = FrontendDataSerializer({
        'user': user if user.is_authenticated else None,
        'stat': stat_service.get_stat(),
        'last_sync_date': date_to_js_unix_time(TempData.objects.get().last_sync_date),
        'config': {
            'project_version': settings.VERSION,
            'group_link': vk_api_service.get_group_url()
        }
    })

    data = {
        'debug': settings.DEBUG,
        'google_analytics_id': settings.GOOGLE_ANALYTICS_ID,
        'frontend_data': encode_json(serializer.data)
    }

    if settings.DEBUG:
        host = 'http://192.168.1.100:8080'
        data['js_files'] = [
            f'{host}/js/app.js',
            f'{host}/js/chunk-vendors.js'
        ]
        data['css_files'] = []
    else:
        data['js_files'] = _get_files('js', 'js')
        data['css_files'] = _get_files('css', 'css')

    return data


def _get_files(dir_name: str, ext: str) -> List[str]:
    path = os.path.join(settings.BASE_DIR, 'app', 'static', 'front', dir_name)
    if not os.path.exists(path):
        os.makedirs(path)

    return [static(f'/front/{dir_name}/{f}') for f in os.listdir(path) if f.split('.')[-1] == ext]
