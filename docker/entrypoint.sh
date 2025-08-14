#!/bin/sh
set -e

python manage.py migrate --noinput || true

if [ "${ENABLE_CRON}" = "1" ]; then
  python manage.py crontab remove || true
  python manage.py crontab add

  service cron start || cron

  tail -F /var/log/cron.log &
else
  echo "Cron disabled (ENABLE_CRON!=1)."
fi

exec "$@"
