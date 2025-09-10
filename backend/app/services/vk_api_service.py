from django.conf import settings
from vk_api.vk_api import VkApiMethod, VkApi

from app.models import Config


def get_authorize_url() -> str:
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


def _get_api() -> VkApiMethod:
    config = Config.objects.get()
    vk_session = VkApi(token=config.comment_access_token)
    return vk_session.get_api()


def get_group_url() -> str:
    config = Config.objects.get()
    return f'{settings.VK_LINK}/club{config.group_id}'


def get_post_url(post_id) -> str:
    config = Config.objects.get()
    return f'{get_group_url()}?w=wall{config.negative_group_id}_{post_id}'


def get_wall_posts(offset: int, count: int) -> dict:
    config = Config.objects.get()
    return _get_api().wall.get(owner_id=config.negative_group_id, offset=offset, count=count)


def get_user(user_id: int) -> dict:
    return _get_api().users.get(user_ids=user_id, fields=['sex', 'photo_50', 'photo_100'])[0]


def get_group(group_id: int) -> dict:
    return _get_api().groups.getById(group_id=group_id)[0]


def create_post(message: str) -> dict:
    config = Config.objects.get()
    return _get_api().wall.post(
        owner_id=config.negative_group_id,
        message=message,
        signed=True,
        from_group=1 if config.comment_from_group else 0
    )


def add_comment_to_post(post_vk_id: int, message: str) -> dict:
    config = Config.objects.get()
    return _get_api().wall.create_comment(
        post_id=post_vk_id,
        owner_id=config.negative_group_id,
        message=message,
        from_group=config.group_id if config.comment_from_group else 0
    )
