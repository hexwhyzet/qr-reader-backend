#!/bin/sh
set -e

python manage.py migrate --noinput || true

if [ "${ENABLE_CRON}" = "1" ]; then
  python manage.py run_scheduler &
else
  echo "Cron disabled (ENABLE_CRON!=1)."
fi

exec "$@"
