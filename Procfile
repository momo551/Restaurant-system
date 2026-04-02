web: export PYTHONPATH=$PYTHONPATH:$(pwd)/backend && python backend/manage.py migrate --noinput && gunicorn --bind 0.0.0.0:$PORT --chdir backend core.wsgi:application
worker: celery -A core worker -l info -P prefork -c 2
beat: celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
