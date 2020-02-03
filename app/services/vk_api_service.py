import vk_api
from vk_api.vk_api import VkApiMethod

from app.models import Config


def _api() -> VkApiMethod:
    config = Config.objects.get()
    vk_session = vk_api.VkApi(token=config.comment_access_token)
    return vk_session.get_api()


def wall_get(offset: int, count: int) -> dict:
    config = Config.objects.get()
    return _api().wall.get(owner_id=config.negative_group_id, offset=offset, count=count)
