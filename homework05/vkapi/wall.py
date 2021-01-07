import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize
from requests.api import post
from vkapi import config, session
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

    if fields:
        code_fields = "?".join(fields)
    else:
        code_fields = ""
    if max_count <= 100:
        code = f"""
        return API.wall.get({{
            "owner_id": "{owner_id}",
            "domain": "{domain}",
            "offset": {offset},
            "count": {max_count},
            "filter": "{filter}",
            "extended": {extended},
            "fields": "{code_fields}",
            "v": {config.VK_CONFIG["version"]}
        }}).items;
        """
    else:
        if max_count > 2500:
            max_count = 2500
        code = f"""
        var wall_records = [];
        var offset = 100 + {offset};
        var count = {count};
        var max_offset = offset + {max_count};
        while (offset < max_offset && wall_records.length <= offset && offset-{offset} < {max_count}) {{
            if ({max_count} - wall_records.length < 100) {{
                count = {max_count} - wall_records.length;
            }};
            wall_records = wall_records + API.wall.get({{
                "owner_id": "{owner_id}",
                "domain": "{domain}",
                "offset": offset,
                "count": count,
                "filter": "{filter}",
                "extended": {extended},
                "fields": "{code_fields}",
                "v": {config.VK_CONFIG["version"]}
            }}).items;
            offset = offset + 100;
        }};
        return wall_records;
        """

    response = session.post(
        url="execute",
        data={
            "code": code,
            "access_token": config.VK_CONFIG["access_token"],
            "v": config.VK_CONFIG["version"],
        },
    ).json()
    if "response" in response:
        return response["response"]
    raise APIError


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
    response = session.post(
        url="execute",
        data={
            "code": f"""
            return API.wall.get({{
            "owner_id": "{owner_id}",
            "domain": "{domain}",
            "offset": {offset},
            "count": "1",
            "filter": "{filter}",
            "extended": {extended},
            "v": {config.VK_CONFIG["version"]}
            }});
            """,
            "access_token": config.VK_CONFIG["access_token"],
            "v": config.VK_CONFIG["version"],
        },
    ).json()
    if "error" in response:
        raise APIError
    posts = response["response"]
    if response["response"]["count"] - offset > count and count != 0:
        max_count = count
    else:
        max_count = response["response"]["count"] - offset
    if max_count == 0:
        return json_normalize(posts["items"])
    window = range(0, max_count, 100)
    if progress:
        window = progress(window)
    num_records = max_count - len(posts)
    for _ in window:
        try:
            posts2500 = get_posts_2500(
                owner_id=owner_id,
                domain=domain,
                offset=offset + len(posts),
                max_count=num_records,
                filter=filter,
                extended=extended,
                fields=fields,
            )
            posts.update(posts2500)
            if not (max_count - len(posts)) > num_records:
                num_records = max_count - len(posts)
        except:
            raise APIError
        time.sleep(0.34)

    return json_normalize(posts["items"])
