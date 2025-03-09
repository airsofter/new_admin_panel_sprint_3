import time
import logging
from functools import wraps
from typing import Any, Callable


def backoff(
    start_sleep_time: float = 0.1,
    factor: float = 2,
    border_sleep_time: float = 10,
    max_attempts: int = 10
) -> Callable:

    def func_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def inner(self, *args: Any, **kwargs: Any) -> Any:
            logging.info(f"Аргументы: {args}, Ключевые аргументы: {kwargs}")
            attempt = 0
            delay = start_sleep_time

            while attempt < max_attempts:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    attempt += 1
                    logging.warning(f"Попытка {attempt}: Ошибка в {func.__name__}: {e}")

                    if attempt >= max_attempts:
                        logging.error(f"Превышено максимальное количество попыток ({max_attempts})")
                        raise e

                    if delay >= border_sleep_time:
                        delay = border_sleep_time
                    else:
                        delay = start_sleep_time * (factor**attempt)

                    logging.info(f"Повтор через {delay:.2f} секунд")
                    time.sleep(delay)

        return inner

    return func_wrapper
