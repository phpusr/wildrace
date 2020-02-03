import vk_api
from vk_api.vk_api import VkApiMethod, VkApi
from django.conf import settings

from app.models import Config


def authorize_url() -> str:
    oauth_url = 'https://oauth.vk.com'
    params = {
        'client_id': settings.VK_APP_ID,
        'display': 'page',
        'redirect_uri': f'{oauth_url}/blank.html',
        'scope': 'wall,offline',
        'response_type': 'token',
        'v': VkApi().api_version
    }
    params_str = '&'.join([f'{key}={value}' for key, value in params.items()])
    return f'{oauth_url}/authorize?{params_str}'


def _api() -> VkApiMethod:
    config = Config.objects.get()
    vk_session = VkApi(token=config.comment_access_token)
    return vk_session.get_api()


def wall_get(offset: int, count: int) -> dict:
    config = Config.objects.get()
    return _api().wall.get(owner_id=config.negative_group_id, offset=offset, count=count)
