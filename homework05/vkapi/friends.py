import dataclasses
import math
import time
import typing as tp

from vkapi import session
from vkapi.config import VK_CONFIG
from vkapi.exceptions import APIError

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.Union[tp.List[int], tp.List[tp.Dict[str, tp.Any]]]


def get_friends(
    user_id: tp.Optional[int],
    count: int = 5000,
    offset: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).

    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Список идентификаторов друзей пользователя или список пользователей.
    """
    params = {
        "access_token": VK_CONFIG["access_token"],
        "v": VK_CONFIG["version"],
        "count": count,
        "user_id": user_id if user_id is not None else "",
        "fields": ",".join(fields) if fields is not None else "",
        "offset": offset,
    }
    response = session.get("friends.get", params=params)
    if "error" in response.json() or not response.ok:
        raise APIError(response.json()["error"]["error_msg"])
    return FriendsResponse(**response.json()["response"])


class MutualFriends(tp.TypedDict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Optional[tp.List[int]] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.Union[tp.List[int], tp.List[MutualFriends]]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.

    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    if target_uids is None:
        params = {
            "access_token": VK_CONFIG["access_token"],
            "v": VK_CONFIG["version"],
            "source_uid": source_uid if source_uid is not None else "",
            "target_uid": target_uid,
            "order": order,
        }
        response = session.get(f"friends.getMutual", params=params)
        if "error" in response.json() or not response.ok:
            raise APIError(response.json()["error"]["error_msg"])
        return response.json()["response"]

    responses = []
    if progress is None:
        progress = lambda x: x
    for mi in progress(range(((len(target_uids) + 99) // 100))):
        params = {
            "access_token": VK_CONFIG["access_token"],
            "v": VK_CONFIG["version"],
            "target_uids": ",".join(map(str, target_uids)),
            "order": order,
            "count": count if count is not None else "",
            "offset": offset + mi * 100,
        }
        response = session.get(f"friends.getMutual", params=params)
        if "error" in response.json() or not response.ok:
            raise APIError(response.json()["error"]["error_msg"])
        for na in response.json()["response"]:
            responses.append(
                MutualFriends(
                    id=na["id"],
                    common_friends=na["common_friends"],
                    common_count=na["common_count"],
                )
            )
        if mi % 3 == 2:
            time.sleep(1)
    return responses