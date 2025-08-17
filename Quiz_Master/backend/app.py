from flask import Flask, request, jsonify, session
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from create_app import create_app, db
from models import User, Subject, Chapter, Quiz, Question, Score
from celery_worker import celery
from celery.schedules import crontab
from tasks.export_admin_csv import export_admin_csv
from tasks.export_user_csv import export_user_csv

app = create_app()

celery.conf.beat_schedule = {
    'send-daily-reminders-every-evening': {
        'task': 'tasks.daily_reminder.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),
    },
    'send-monthly-reports': {
        'task': 'tasks.monthly_report.send_monthly_reports',
        'schedule': crontab(hour=15, minute=15, day_of_month=1),
    }
}
celery.conf.timezone = 'Asia/Kolkata'

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='23F3001436@ds.study.iitm.ac.in').first():
        admin = User(
            username='23F3001436@ds.study.iitm.ac.in',
            password='admin123',
            full_name='Quiz Master',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return jsonify({"message": "Welcome to Quiz Master API"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        return jsonify({"message": "Login successful", "user_id": user.id, "is_admin": user.is_admin})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = User(
            username=data['username'],
            password=data['password'],
            full_name=data['full_name'],
            qualification=data['qualification'],
            dob=datetime.strptime(data['dob'], '%Y-%m-%d')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Registration successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/subjects/<int:subject_id>', methods=['GET'])
def get_subject_by_id(subject_id):
    """Retrieves a single subject by its ID."""
    print(f"DEBUG: Fetching subject with ID: {subject_id}")
    subject = Subject.query.get(subject_id)
    if not subject:
        print(f"DEBUG: Subject with ID {subject_id} not found.")
        return jsonify({"error": "Subject not found"}), 404
    print(f"DEBUG: Found subject: {subject.name}")
    return jsonify({
        "subject": {"id": subject.id, "name": subject.name, "description": subject.description}
    })

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    print("DEBUG: Session at /admin/dashboard:", session)
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    subjects = Subject.query.all()
    users = User.query.filter_by(is_admin=False).all()
    return jsonify({
        "subjects": [{"id": s.id, "name": s.name, "description": s.description} for s in subjects],
        "users": [{"id": u.id, "username": u.username, "full_name": u.full_name, "qualification":u.qualification} for u in users]
    })

@app.route('/admin/subject/new', methods=['POST'])
def new_subject():
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    subject = Subject(name=data['name'], description=data['description'])
    db.session.add(subject)
    db.session.commit()
    return jsonify({"message": "Subject created"})

@app.route('/admin/subject/edit/<int:subject_id>', methods=['PUT'])
def edit_subject(subject_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    subject = Subject.query.get_or_404(subject_id)
    subject.name = data['name']
    subject.description = data['description']
    db.session.commit()
    return jsonify({"message": "Subject updated"})

@app.route('/admin/subject/delete/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({"message": "Subject deleted"})

@app.route('/admin/chapter/<int:chapter_id>', methods=['GET'])
def get_chapter_details(chapter_id):
    """Retrieves details for a specific chapter. Requires admin privileges."""
    if not session.get("is_admin"):
        return jsonify({"error": "Forbidden"}), 403
    
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"error": "Chapter not found"}), 404
    
    return jsonify({
        "id": chapter.id,
        "name": chapter.name,
        "description": chapter.description,
        "subject_id": chapter.subject_id
    })

@app.route('/admin/chapter/new/<int:subject_id>', methods=['POST'])
def new_chapter(subject_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    chapter = Chapter(subject_id=subject_id, name=data['name'], description=data['description'])
    db.session.add(chapter)
    db.session.commit()
    return jsonify({"message": "Chapter created"})

@app.route('/admin/chapter/edit/<int:chapter_id>', methods=['PUT'])
def edit_chapter(chapter_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter.name = data['name']
    chapter.description = data['description']
    db.session.commit()
    return jsonify({"message": "Chapter updated"})

@app.route('/admin/chapter/delete/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({"message": "Chapter deleted"})

@app.route('/admin/quiz/new/<int:chapter_id>', methods=['POST'])
def new_quiz(chapter_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    quiz = Quiz(
        chapter_id=chapter_id,
        date_of_quiz=datetime.strptime(data['date_of_quiz'], '%Y-%m-%d'),
        time_duration=data['time_duration'],
        remarks=data['remarks']
    )
    db.session.add(quiz)
    db.session.commit()
    return jsonify({"message": "Quiz created", "quiz_id": quiz.id})

@app.route('/admin/quiz/edit/<int:quiz_id>', methods=['PUT'])
def edit_quiz(quiz_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz.date_of_quiz = datetime.strptime(data['date_of_quiz'], '%Y-%m-%d')
    quiz.time_duration = data['time_duration']
    quiz.remarks = data['remarks']
    db.session.commit()
    return jsonify({"message": "Quiz updated"})

@app.route('/admin/quiz/delete/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({"message": "Quiz deleted"})

@app.route('/admin/subject/<int:subject_id>/chapters', methods=['GET'])
def get_chapters_by_subject(subject_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Forbidden"}), 403
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify({
        "subject_id": subject_id,
        "chapters": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description
            } for c in chapters
        ]
    })

@app.route('/admin/chapter/<int:chapter_id>/quizzes', methods=['GET'])
def get_quizzes_by_chapter(chapter_id):
    """
    Retrieves quizzes for a specific chapter. Requires admin privileges.
    """
    print(f"DEBUG: Session at /admin/chapter/{chapter_id}/quizzes: {dict(session)}")
    if not session.get("is_admin"):
        print(f"DEBUG: Unauthorized access to /admin/chapter/{chapter_id}/quizzes: is_admin is False or missing.")
        return jsonify({"error": "Forbidden"}), 403
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    print(f"DEBUG: Found {len(quizzes)} quizzes for chapter {chapter_id}.")
    return jsonify({
        "chapter_id": chapter_id,
        "quizzes": [
            {
                "id": q.id,
                "date_of_quiz": q.date_of_quiz.isoformat(),
                "time_duration": q.time_duration,
                "remarks": q.remarks
            } for q in quizzes
        ]
    })

@app.route('/admin/quiz/<int:quiz_id>/questions', methods=['GET'])
def get_quiz_questions_admin(quiz_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([
        {
            "id": q.id,
            "question_statement": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4],
            "correct_option": q.correct_option,
            "marks": q.marks 
        } for q in questions
    ])

@app.route('/admin/question/new/<int:quiz_id>', methods=['POST'])
def new_question(quiz_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    question = Question(
        quiz_id=quiz_id,
        question_statement=data['question_statement'],
        option1=data['option1'],
        option2=data['option2'],
        option3=data['option3'],
        option4=data['option4'],
        correct_option=int(data['correct_option']),
        marks=int(data.get('marks', 1))
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({"message": "Question added"})

@app.route('/admin/question/edit/<int:question_id>', methods=['PUT'])
def edit_question(question_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    question = Question.query.get_or_404(question_id)
    question.question_statement = data['question_statement']
    question.option1 = data['option1']
    question.option2 = data['option2']
    question.option3 = data['option3']
    question.option4 = data['option4']
    question.correct_option = int(data['correct_option'])
    question.marks = int(data.get('marks', question.marks))
    db.session.commit()
    return jsonify({"message": "Question updated"})

@app.route('/admin/question/delete/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question deleted"})

@app.route('/admin/attempts')
def view_attempts():
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    attempts = Score.query.all()
    attempts_data = []
    for attempt in attempts:
        user = User.query.get(attempt.user_id)
        quiz = Quiz.query.get(attempt.quiz_id)
       
        
        total_marks_possible = 0
        SubjectName= "N/A"

        if quiz:
            questions = Question.query.filter_by(quiz_id=quiz.id).all()
            for question in questions:
                total_marks_possible += question.marks
            
            # Fetch chapter and then subject
            chapter = Chapter.query.get(quiz.chapter_id)
            if chapter:
                subject = Subject.query.get(chapter.subject_id)
                if subject:
                    SubjectName = subject.name

        attempts_data.append({
            "user_id": attempt.user_id,
            "username": user.username if user else "N/A",
            "full_name": user.full_name if user else "N/A",
            "quiz_id": attempt.quiz_id,
            "score": attempt.total_scored,
            "total_marks": total_marks_possible,
            "subject_name": SubjectName,
            "timestamp": attempt.time_stamp_of_attempt.isoformat()
        })
    return jsonify(attempts_data)

@app.route('/admin/export/csv', methods=['GET'])
def export_all_csv():
    print("SESSION AT EXPORT CSV:", session) 
    admin = db.session.get(User, session.get("user_id"))
    if not admin or not admin.is_admin:
        return jsonify({"error": "Unauthorized"}), 401
    export_admin_csv.delay(admin.username)
    return jsonify({"message": "Export started. You'll receive the CSV via email."})

@app.route('/user/<int:user_id>/dashboard')
def user_dashboard(user_id):
    """User dashboard showing subjects and scores."""
    print(f"DEBUG: Session at /user/{user_id}/dashboard: {dict(session)}")
    if 'user_id' not in session or session['user_id'] != user_id:
        print(f"DEBUG: Unauthorized access to /user/{user_id}/dashboard: Session user ID mismatch or not logged in.")
        return jsonify({"error": "Unauthorized access to this user's dashboard"}), 401

    print(f"DEBUG: Authorized access to /user/{user_id}/dashboard. Fetching user data.")
    user = User.query.get_or_404(user_id)
    subjects = Subject.query.all()
    scores = Score.query.filter_by(user_id=user_id).all()
    
    enhanced_scores = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        total_marks_possible = 0
        subject_name = "N/A"

        if quiz:
            questions = Question.query.filter_by(quiz_id=quiz.id).all()
            total_marks_possible = sum(q.marks for q in questions)
            
            chapter = Chapter.query.get(quiz.chapter_id)
            if chapter:
                subject = Subject.query.get(chapter.subject_id)
                if subject:
                    subject_name = subject.name

        enhanced_scores.append({
            "quiz_id": score.quiz_id,
            "total_scored": score.total_scored,
            "time_stamp_of_attempt": score.time_stamp_of_attempt.isoformat(),
            "total_marks_possible": total_marks_possible,
            "subject_name": subject_name
        })

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "qualification": user.qualification
        },
        "subjects": [{"id": s.id, "name": s.name, "description": s.description} for s in subjects],
        "scores": enhanced_scores
    })
@app.route('/user/<int:user_id>/quizzes/<int:subject_id>')
def select_quiz(user_id, subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    quiz_ids = [chapter.id for chapter in chapters]
    quizzes = Quiz.query.filter(Quiz.chapter_id.in_(quiz_ids)).all()
    return jsonify([
        {
            "id": q.id,
            "name": f"Quiz {q.id} for {subject.name}",
            "chapter_id": q.chapter_id,
            "date_of_quiz": q.date_of_quiz.isoformat(),
            "time_duration": q.time_duration,
            "remarks": q.remarks
        } for q in quizzes
    ])

@app.route('/user/<int:user_id>/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(user_id, quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'GET':
        return jsonify([
            {
                "id": q.id,
                "question_statement": q.question_statement,
                "options": [q.option1, q.option2, q.option3, q.option4],
                "marks": q.marks
            } for q in questions
        ])

    data = request.json
    answers = data.get("answers", {})
    total_scored = 0
    total_marks_possible = 0

    for question in questions:
        total_marks_possible += question.marks
        if str(question.id) in answers and int(answers[str(question.id)]) == question.correct_option:
            total_scored += question.marks

    score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        time_stamp_of_attempt=datetime.now(),
        total_scored=total_scored
    )
    db.session.add(score)
    db.session.commit()
    return jsonify({"message": "Quiz completed", "score": total_scored, "total_marks": total_marks_possible})

@app.route('/user/<int:user_id>/export/my_csv', methods=['GET'])
def export_my_csv(user_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if session["user_id"] != user_id:
        return jsonify({"error": "Forbidden"}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    from tasks.export_user_csv import export_user_csv
    export_user_csv.delay(user.id, user.username, user.full_name)

    return jsonify({"message": "Export started. You'll receive an email shortly."})

@app.route('/quizzes/<int:quiz_id>', methods=['GET'])
def get_quiz_meta(quiz_id):
    """Retrieves metadata for a specific quiz."""
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        "id": quiz.id,
        "date_of_quiz": quiz.date_of_quiz.isoformat(),
        "time_duration": quiz.time_duration,
        "remarks": quiz.remarks,
        "chapter_id": quiz.chapter_id
    })

if __name__ == '__main__':
    app.run(debug=True)