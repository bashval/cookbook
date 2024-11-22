#! usr/bin/sh
echo "Collect static files"
python manage.py collectstatic
cp -r /app/collected_static/. /backend_static/static/

# Verify that Postgres is healthy before applying the migrations and running the Django development server
apt-get update && apt-get install -y netcat-traditional

echo "Waiting for Postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "PostgreSQL started"

echo "Apply database migrations"
python manage.py makemigrations
python ./manage.py migrate


echo "Load csv"
python manage.py load_csv static_dev/data/ingredients.csv
python manage.py load_csv static_dev/data/tags.csv

gunicorn foodgram_backend.wsgi:application --bind 0.0.0.0:8000
