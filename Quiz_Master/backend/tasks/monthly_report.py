from datetime import datetime, timedelta
from models import db, User, Score, Quiz, Chapter, Subject, Question
from mail_util import send_mail
from celery_worker import celery
from sqlalchemy import func
import os
from weasyprint import HTML

@celery.task(name='tasks.monthly_report.send_monthly_reports')
def send_monthly_reports():
    print("Running monthly report job...")

    today = datetime.now()
    first_day_of_month = datetime(today.year, today.month, 1)
    last_month = first_day_of_month - timedelta(days=1)
    month_start = datetime(last_month.year, last_month.month, 1)
    month_end = datetime(last_month.year, last_month.month, last_month.day, 23, 59, 59)

    users = User.query.filter_by(is_admin=False).all()

    user_scores = db.session.query(
        Score.user_id, func.sum(Score.total_scored).label('total')
    ).filter(
        Score.time_stamp_of_attempt >= month_start,
        Score.time_stamp_of_attempt <= month_end
    ).group_by(Score.user_id).order_by(func.sum(Score.total_scored).desc()).all()
    rankings = [uid for uid, _ in user_scores]
    ranked_users_count = len(rankings)

    for user in users:
        scores = Score.query.filter(
            Score.user_id == user.id,
            Score.time_stamp_of_attempt >= month_start,
            Score.time_stamp_of_attempt <= month_end
        ).all()

        if not scores:
            send_mail(
                to_email=user.username,
                subject="Monthly Quiz Report - No Activity",
                body=f"""
Hi {user.full_name},

We noticed you haven't taken any quizzes between {month_start.date()} and {month_end.date()}.

No worries — new quizzes are coming! We encourage you to log in and participate this month.

Best wishes,  
Quiz Master
"""
            )
            print(f"No activity mail sent to {user.username}")
            continue

        total_quizzes = len(scores)
        total_score = sum(s.total_scored for s in scores)
        avg_score = total_score / total_quizzes

        try:
            user_rank = rankings.index(user.id) + 1
        except ValueError:
            user_rank = "N/A"

        total_possible_score = 0
        quiz_details = []
        for s in scores:
            quiz = Quiz.query.get(s.quiz_id)
            
            subject_name = "N/A"
            chapter_name = "N/A"
            
            if quiz and quiz.chapter:
                chapter_name = quiz.chapter.name
                if quiz.chapter.subject:
                    subject_name = quiz.chapter.subject.name
            
            quiz_questions = Question.query.filter_by(quiz_id=s.quiz_id).all()
            quiz_total_marks = sum(q.marks for q in quiz_questions)
            total_possible_score += quiz_total_marks

            quiz_details.append({
                'subject_name': subject_name,
                'chapter_name': chapter_name,
                'quiz_id': s.quiz_id,
                'user_score': s.total_scored,
                'quiz_total_marks': quiz_total_marks,
                'attempt_date': s.time_stamp_of_attempt.strftime('%Y-%m-%d')
            })

        avg_percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0

        report_body = f"""
Hi {user.full_name},

Here's your quiz activity report for {month_start.strftime('%B %Y')}:

- Quizzes Taken: {total_quizzes}
- Total Score: {total_score} out of {total_possible_score}
- Average Score: {avg_score:.2f}
- Average Percentage: {avg_percentage:.2f}%
- Your Rank: {user_rank} out of {ranked_users_count}

Keep up the good work! You can find a detailed report attached.
Best wishes,  
Quiz Master
"""

        rows = ""
        for detail in quiz_details:
            rows += f"<tr><td>{detail['subject_name']}</td><td>{detail['chapter_name']}</td><td>{detail['quiz_id']}</td><td>{detail['user_score']}</td><td>{detail['quiz_total_marks']}</td><td>{detail['attempt_date']}</td></tr>"

        html_content = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h2>Monthly Report - {month_start.strftime('%B %Y')}</h2>
    <p><strong>User:</strong> {user.full_name} ({user.username})</p>
    <p><strong>Total Quizzes:</strong> {total_quizzes}</p>
    <p><strong>Total Score:</strong> {total_score} out of {total_possible_score}</p>
    <p><strong>Average Score:</strong> {avg_score:.2f}</p>
    <p><strong>Average Percentage:</strong> {avg_percentage:.2f}%</p>
    <p><strong>Your Rank:</strong> {user_rank} out of {ranked_users_count}</p>

    <table>
        <tr><th>Subject Name</th><th>Chapter Name</th><th>Quiz ID</th><th>User Score</th><th>Max Score</th><th>Date Attempted</th></tr>
        {rows}
    </table>
</body>
</html>
"""

        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        base_filename = f"{user.username}_{month_start.strftime('%Y_%m')}"
        html_path = os.path.join(report_dir, f"{base_filename}.html")
        pdf_path = os.path.join(report_dir, f"{base_filename}.pdf")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        try:
            HTML(string=html_content).write_pdf(pdf_path)
            
            send_mail(
                to_email=user.username,
                subject=f"Your Monthly Quiz Report - {month_start.strftime('%B %Y')}",
                body=report_body,
                attachments=[html_path, pdf_path]
            )
            print(f"Report sent to {user.username}")
        except Exception as e:
            print(f"Error sending report to {user.username}: {e}")
