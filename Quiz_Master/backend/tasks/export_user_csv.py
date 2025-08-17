import csv
import os
from datetime import datetime
from sqlalchemy import func

from create_app import create_app, db
from models import User, Score, Quiz, Chapter, Subject, Question
from mail_util import send_mail
from celery_worker import celery

flask_app_instance = create_app()

@celery.task
def export_user_csv(user_id, username, full_name):
    """
    Celery task to export a specific user's quiz scores to a CSV file
    and send it to their email, including the subject name and user's rank.
    """
    with flask_app_instance.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"ERROR: User with ID {user_id} not found for CSV export.")
            return

        scores = Score.query.filter_by(user_id=user_id).all()

        user_total_score = sum(score.total_scored for score in scores)

        all_user_scores_query = db.session.query(
            User.id,
            func.sum(Score.total_scored).label('total_score')
        ).join(Score).filter(User.is_admin == False).group_by(User.id).order_by(func.sum(Score.total_scored).desc()).all()

        user_rank = "N/A"
        for i, (uid, total_score) in enumerate(all_user_scores_query):
            if uid == user_id:
                user_rank = i + 1
                break

        csv_filename = f"user_quiz_scores_{username.replace('@', '_').replace('.', '_')}.csv"
        
        instance_path = os.path.join(flask_app_instance.root_path, 'instance')
        os.makedirs(instance_path, exist_ok=True)
        csv_filepath = os.path.join(instance_path, csv_filename)

        try:
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Quiz ID', 'Subject', 'Score', 'Max Score', 'Attempt Timestamp']) # Added 'Max Score'

                for score in scores:
                    subject_name = "N/A"
                    total_marks_possible = 0
                    quiz = Quiz.query.get(score.quiz_id)
                    if quiz:
                        questions = Question.query.filter_by(quiz_id=quiz.id).all()
                        total_marks_possible = sum(q.marks for q in questions)

                        chapter = Chapter.query.get(quiz.chapter_id)
                        if chapter:
                            subject = Subject.query.get(chapter.subject_id)
                            if subject:
                                subject_name = subject.name
                    
                    csv_writer.writerow([
                        score.quiz_id,
                        subject_name,
                        score.total_scored,
                        total_marks_possible,
                        score.time_stamp_of_attempt.isoformat()
                    ])
            
            subject_email = "Your Quiz Master Scores Export"
            body_email = f"Dear {full_name},\n\nPlease find your quiz scores attached.\n\n"
            if user_rank != "N/A":
                body_email += f"Your overall rank based on total score is: {user_rank} out of {len(all_user_scores_query)} users.\n\n"
            body_email += "Regards,\nQuiz Master Team"
            
            send_mail(user.username, subject_email, body_email, attachments=[csv_filepath])
            
            print(f"INFO: Successfully exported CSV for user {username} and sent email to {user.username}.")

        except Exception as e:
            print(f"ERROR: Failed to export CSV or send email for user {username}: {e}")
        finally:
            if os.path.exists(csv_filepath):
                os.remove(csv_filepath)
                print(f"Cleaned up temporary CSV file: {csv_filepath}")