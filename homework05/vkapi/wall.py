import math
import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize
from vkapi import session
from vkapi.config import VK_CONFIG
from vkapi.exceptions import APIError


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> tp.Dict[str, tp.Any]:
    script = f"""
                var i = 0; 
                var result = [];
                while (i < {max_count}){{
                    if ({offset}+i+100 > {count}){{
                        result.push(API.wall.get({{
                            "owner_id": "{owner_id}",
                            "domain": "{domain}",
                            "offset": "{offset} +i",
                            "count": "{count}-(i+{offset})",
                            "filter": "{filter}",
                            "extended": "{extended}",
                            "fields": "{fields}"
                        }}));
                    }} 
                    result.push(API.wall.get({{
                        "owner_id": "{owner_id}",
                        "domain": "{domain}",
                        "offset": "{offset} +i",
                        "count": "{count}",
                        "filter": "{filter}",
                        "extended": "{extended}",
                        "fields": "{fields}"
                    }}));
                    i = i + {max_count};
                }}
                return result;
            """
    data = {
        "code": script,
        "access_token": VK_CONFIG["access_token"],
        "v": VK_CONFIG["version"],
    }
    response = session.post("execute", data=data)
    if "error" in response.json() or not response.ok:
        raise APIError(response.json()["error"]["error_msg"])
    return response.json()["response"]["items"]


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """
    df = []
    response = session.post(
        "execute",
        data={
            "code": f'return {{"count": API.wall.get({{"owner_id": "{owner_id}","domain": "{domain}","offset": "0","count": "1","filter": "{filter}"}}).count}};',
            "access_token": VK_CONFIG["access_token"],
            "v": VK_CONFIG["version"],
        },
    )
    if "error" in response.json() or not response.ok:
        raise APIError(response.json()["error"]["error_msg"])
    if count != 0:
        count = min(count, response.json()["response"]["count"])
    else:
        count = response.json()["response"]["count"]
    if progress is None:
        progress = lambda x: x

    for mi in progress(range((count + max_count - 1) // max_count)):
        df.append(
            get_posts_2500(
                owner_id,
                domain,
                offset + mi * max_count,
                count,
                max_count,
                filter,
                extended,
                fields,
            )
        )
        if mi % 3 == 1:
            time.sleep(1)
    return json_normalize(df)