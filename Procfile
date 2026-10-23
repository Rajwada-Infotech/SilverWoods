web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn silverwoods.wsgi --log-file - --worker-class gthread --workers 2 --threads 4 --timeout 300
