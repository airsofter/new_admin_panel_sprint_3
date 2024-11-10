FROM python:3.12

WORKDIR /opt/app

COPY pyproject.toml pyproject.toml

RUN  mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install poetry \
     && poetry config virtualenvs.create false \
     && poetry install --no-interaction --no-ansi

COPY project/simple_project/app .


ENTRYPOINT ["sh", "run_uwsgi.sh"]
