#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

apt-get update
apt-get install -y gettext

python manage.py compilemessages
python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --strict --ini uwsgi/uwsgi.ini
