import csv
import os
from datetime import datetime
from sqlalchemy import func

from create_app import create_app, db
from models import User, Score, Quiz, Chapter, Subject, Question
from mail_util import send_mail
from celery_worker import celery

flask_app_instance = create_app()

@celery.task(name='tasks.export_admin_csv.export_admin_csv')
def export_admin_csv(admin_email):
    """
    Celery task to export all admin data to a CSV file, including user ranks,
    and send it to the admin's email with summary insights.
    """
    with flask_app_instance.app_context():
        
        results = db.session.query(
            User.id,
            User.full_name,
            User.username,
            User.qualification,
            func.count(Score.id).label("quizzes_taken"),
            func.sum(Score.total_scored).label("total_score_sum"),
            func.avg(Score.total_scored).label("average_attempt_score")
        ).join(Score).filter(User.is_admin == False).group_by(User.id, User.full_name, User.username, User.qualification).all()

        user_data_for_ranking = []
        for r in results:
            user_data_for_ranking.append({
                'user_id': r.id,
                'full_name': r.full_name,
                'username': r.username,
                'qualification': r.qualification,
                'quizzes_taken': r.quizzes_taken,
                'total_score_sum': r.total_score_sum,
                'average_attempt_score': r.average_attempt_score
            })
        
        user_data_for_ranking.sort(key=lambda x: x['total_score_sum'], reverse=True)

        for i, user_entry in enumerate(user_data_for_ranking):
            user_entry['rank'] = i + 1

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        csv_filename = f"admin_report_{timestamp}.csv"
        
        exports_path = os.path.join(flask_app_instance.root_path, 'exports')
        os.makedirs(exports_path, exist_ok=True)
        csv_filepath = os.path.join(exports_path, csv_filename)

        try:
            with open(csv_filepath, mode="w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                
                writer.writerow([
                    'User ID', 'Full Name', 'Quizzes Taken', 'Average Score'
                ])

                for user_entry in user_data_for_ranking:
                    
                    writer.writerow([
                        user_entry['user_id'],
                        user_entry['full_name'],
                        user_entry['quizzes_taken'],
                        round(user_entry['average_attempt_score'], 2)
                    ])

            total_registered_users = User.query.filter(User.is_admin == False).count()
            total_users_with_attempts = len(user_data_for_ranking)
            overall_quizzes_taken = sum(u['quizzes_taken'] for u in user_data_for_ranking)
            overall_total_score = sum(u['total_score_sum'] for u in user_data_for_ranking)
            
            overall_average_score_across_all_quizzes = 0
            if overall_quizzes_taken > 0:
                all_scores = db.session.query(Score.total_scored).all()
                overall_average_score_across_all_quizzes = sum(s.total_scored for s in all_scores) / overall_quizzes_taken

            top_performers_summary = ""
            if user_data_for_ranking:
                top_3 = user_data_for_ranking[:3]
                top_performers_summary = "\nTop 3 Performers (by Total Score):\n"
                for p in top_3:
                    top_performers_summary += f"- Rank {p['rank']}: {p['full_name']} ({p['username']}) - Total Score: {p['total_score_sum']}, Avg per Quiz: {round(p['average_attempt_score'], 2)}\n"
            else:
                top_performers_summary = "\nNo quiz attempts recorded yet.\n"

            qualification_stats = {}
            for user_entry in user_data_for_ranking:
                qual = user_entry['qualification'] if user_entry['qualification'] else 'Unspecified'
                if qual not in qualification_stats:
                    qualification_stats[qual] = {'users': 0, 'total_score': 0, 'quizzes_taken': 0}
                qualification_stats[qual]['users'] += 1
                qualification_stats[qual]['total_score'] += user_entry['total_score_sum']
                qualification_stats[qual]['quizzes_taken'] += user_entry['quizzes_taken']
            
            qualification_summary = "\nPerformance by Qualification:\n"
            for qual, stats in qualification_stats.items():
                avg_score_for_qual = round(stats['total_score'] / stats['quizzes_taken'], 2) if stats['quizzes_taken'] > 0 else 0
                qualification_summary += f"- {qual}: {stats['users']} users, Total Score: {stats['total_score']}, Avg Score per Quiz: {avg_score_for_qual}\n"


            email_body = f"""
Hi Admin,

Here is your comprehensive quiz activity report.

Summary Insights:
- Total Registered Users (Non-Admin): {total_registered_users}
- Total Users with Quiz Attempts: {total_users_with_attempts}
- Total Quizzes Taken Across All Users: {overall_quizzes_taken}
- Overall Average Score Across All Quizzes: {round(overall_average_score_across_all_quizzes, 2) if overall_quizzes_taken > 0 else 0}

{top_performers_summary}
{qualification_summary}

Please find the detailed CSV export attached.

Regards,
Quiz Master Team
"""

            send_mail(
                to_email=admin_email,
                subject=f"Admin Quiz Summary Report - {timestamp}",
                body=email_body,
                attachments=[csv_filepath]
            )
            print(f"INFO: Successfully exported admin CSV to {admin_email} and sent email.")

        except Exception as e:
            print(f"ERROR: Failed to export admin CSV or send email to {admin_email}: {e}")
        finally:
            if os.path.exists(csv_filepath):
                os.remove(csv_filepath)
                print(f"Cleaned up temporary admin CSV file: {csv_filepath}")