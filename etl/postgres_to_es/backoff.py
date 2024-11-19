import time
import logging
from functools import wraps


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    def func_wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            logging.info(f"Аргументы: {args}, Ключевые аргументы: {kwargs}")
            attempt = 0
            delay = start_sleep_time

            while True:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    attempt += 1
                    logging.warning(f"Попытка {attempt}: Ошибка в {func.__name__}: {e}")

                    if delay >= border_sleep_time:
                        delay = border_sleep_time
                    else:
                        delay = start_sleep_time * (factor**attempt)

                    logging.info(f"Повтор через {delay:.2f} секунд")
                    time.sleep(delay)

        return inner

    return func_wrapper
