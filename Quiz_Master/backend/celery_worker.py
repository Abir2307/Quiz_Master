from celery import Celery
from create_app import create_app, db

flask_app = create_app()
flask_app.app_context().push()

celery = Celery(
    flask_app.import_name,
    backend=flask_app.config['result_backend'],
    broker=flask_app.config['broker_url']
)

celery.conf.update(
    flask_app.config,
    enable_utc=False,
    timezone='Asia/Kolkata',
    imports=['tasks.daily_reminder', 'tasks.monthly_report', 'tasks.export_admin_csv', 'tasks.export_user_csv']
)
