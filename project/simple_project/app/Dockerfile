FROM python:3.10

WORKDIR /opt/app

# COPY run_uwsgi.sh run_uwsgi.sh # TODO удалить
COPY ../../pyproject.toml pyproject.toml
# COPY requirements.txt requirements.txt # TODO удалить
# COPY uwsgi/uwsgi.ini uwsgi.ini  # TODO удалить

RUN  mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install poetry \
     && poetry config virtualenvs.create false \
     && poetry install --no-interaction --no-ansi

COPY . .

ENTRYPOINT ["sh", "run_uwsgi.sh"]
