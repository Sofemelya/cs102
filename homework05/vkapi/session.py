import typing as tp

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from vkapi.config import VK_CONFIG


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, timeout, *args, **kwargs):
        self.timeout = timeout
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


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
        self.base_url = base_url

        retry = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=backoff_factor,
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
        )

        adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retry)
        self.mount(self.base_url, adapter)

    def get(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:  # type:ignore
        return super().get(self.base_url + "/" + url, *args, **kwargs)

    def post(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:  # type:ignore
        return super().post(self.base_url + "/" + url, *args, **kwargs)