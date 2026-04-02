web: (python manage.py migrate --noinput || python backend/manage.py migrate --noinput || true) && (python emergency_reset.py || python backend/emergency_reset.py || true) && (python manage.py collectstatic --noinput || python backend/manage.py collectstatic --noinput || true) && (daphne -b 0.0.0.0 -p $PORT core.asgi:application || daphne -b 0.0.0.0 -p $PORT backend.core.asgi:application)
worker: celery -A core worker -l info -P prefork -c 2
beat: celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
