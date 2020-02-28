from app import settings
from app.models import TempData
from app.serializers import FrontendDataSerializer
from app.services import stat_service, vk_api_service
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


def get_data(user):
    host = 'http://192.168.1.100:8080/' if settings.DEBUG else '/'

    serializer = FrontendDataSerializer({
        'user': user if user.is_authenticated else None,
        'stat': stat_service.get_stat(),
        'last_sync_date': TempData.objects.get().last_sync_date.timestamp() * 1000,
        'config': {
            'project_version': settings.VERSION,
            'group_link': vk_api_service.get_group_url()
        }
    })
    json = CamelCaseJSONRenderer().render(serializer.data).decode('utf-8')

    return {
        'google_analytics_id': '',
        'js_files': [
            f'{host}js/app.js',
            f'{host}js/chunk-vendors.js'
        ],
        'css_files': [],
        'frontend_data': json
    }
