import typing as tp

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry


class Session(requests.Session):
    """
    Сессия.
    :param base_url: Базовый адрес, на который будут выполняться запросы.
    :param timeout: Максимальное время ожидания ответа от сервера.
    :param max_retries: Максимальное число повторных запросов.
    :param backoff_factor: Коэффициент экспоненциального нарастания задержки.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        super().__init__()
        self.retries = Retry(
            total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500]
        )
        self.mount(base_url, HTTPAdapter(max_retries=self.retries))
        self.base_url = base_url
        self.timeout = timeout

    def get(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:  # type: ignore
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        return super().get(f"{self.base_url}/{url}", *args, **kwargs)

    def post(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:  # type: ignore
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        return super().post(f"{self.base_url}/{url}", *args, **kwargs)
