from datetime import datetime
from mail_util import send_mail
from models import db, User, Score, Quiz
from celery_worker import celery

@celery.task(name='tasks.daily_reminder.send_daily_reminders')
def send_daily_reminders():
    print("Running reminder check...")

    today = datetime.now().date()
    users = User.query.filter_by(is_admin=False).all()

    reminders_sent = 0
    errors = []

    for user in users:
        recent_score = Score.query.filter_by(user_id=user.id).order_by(Score.time_stamp_of_attempt.desc()).first()
        last_attempt_date = recent_score.time_stamp_of_attempt.date() if recent_score else None

        new_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= today).all()

        if (not last_attempt_date or last_attempt_date < today) or new_quizzes:
            try:
                send_mail(
                    to_email=user.username,
                    subject="Reminder: New Quiz or Inactivity",
                    body=f"""
Hi {user.full_name},

You have {len(new_quizzes)} upcoming quiz(es), and your last attempt was on {last_attempt_date or 'N/A'}.

Please log in to Quiz Master and complete your quizzes today.

Regards,
Quiz Master
"""
                )
                print(f"Reminder sent to {user.username}")
                reminders_sent += 1
            except Exception as e:
                print(f"Error sending reminder to {user.username}: {e}")
                errors.append((user.username, str(e)))

    return {
        "reminders_sent": reminders_sent,
        "errors": errors
    }
