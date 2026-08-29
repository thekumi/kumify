#!/bin/sh
set -eu

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-moodyduck.settings}"
export PYTHONPATH="${PYTHONPATH:-/app}"

mkdir -p /app/data /app/data/logs
cd /app/data

run_django() {
    python -m django "$@" --settings="${DJANGO_SETTINGS_MODULE}"
}

case "${1:-web}" in
    web)
        run_django migrate --noinput
        run_django collectstatic --noinput
        exec gunicorn moodyduck.wsgi:application \
            --bind 0.0.0.0:9000 \
            --workers "${GUNICORN_WORKERS:-4}" \
            --timeout "${GUNICORN_TIMEOUT:-120}"
        ;;
    manage)
        shift
        exec python -m django "$@" --settings="${DJANGO_SETTINGS_MODULE}"
        ;;
    *)
        exec "$@"
        ;;
esac
