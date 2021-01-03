import datetime as dt
import statistics
import typing as tp

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    ages = []
    now = dt.date.today()
    friends = get_friends(user_id, fields=["bdate"]).items
    for friend in friends:
        try:
            bdate = dt.datetime.strptime(friend["bdate"], "%d.%m.%Y")  # type: ignore
        except (KeyError, ValueError):
            continue
        ages.append(
            now.year
            - bdate.year
            - (now.month < bdate.month or (now.month == bdate.month and now.day < bdate.day))
        )

    if ages:
        return statistics.median(ages)
    return None
