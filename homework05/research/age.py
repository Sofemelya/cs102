import datetime as dt
import statistics
import typing as tp

from dateutil.relativedelta import relativedelta
from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    ages = []
    friends = get_friends(user_id, fields=["bdate"])
    for friend in friends.items:
        try:
            birthdate = dt.datetime.strptime(friend["bdate"], "%d.%m.%Y")  # type: ignore
            age = relativedelta(dt.datetime.now(), birthdate).years
            ages.append(age)
        except (KeyError, ValueError):
            pass
    if not ages:
        return None
    return statistics.median(ages)
