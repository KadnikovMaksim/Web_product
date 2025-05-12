from data.users import Users
from data.questions import Questions
import sozdanie_BD
from flask import Flask, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import sqlalchemy
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired
from flask import render_template
from flask import redirect
from forms.user import LoginForm, RegisterForm, ChangeInfo
from forms.quizes import CreateForm, ChangeForm


from waitress import serve
app = Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = sozdanie_BD.db_session.create_session()
    return db_sess.get(Users, user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = sozdanie_BD.db_session.create_session()
        if db_sess.query(Users).filter(Users.login == form.login.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = Users()
        user.login = form.login.data
        user.about = form.about.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print('f')
    if form.validate_on_submit():
        db_sess = sozdanie_BD.db_session.create_session()
        user = db_sess.query(Users).filter(Users.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me)
            return redirect("/home")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/home', methods=['GET', 'POST'])
@login_required
def main():
    if request.method == 'POST':
        topic = request.form.get('topic')
        question = request.form.get('question')
        subject = request.form.get('subject')

    db_sess = sozdanie_BD.db_session.create_session()
    quests = db_sess.query(Questions).filter(Questions.user_id == current_user.id)
    return render_template('home.html', title='', quests=quests)

@app.route('/home/Create', methods=['GET', 'POST'])
def Create():
    form = CreateForm()
    if form.validate_on_submit():
        db_sess = sozdanie_BD.db_session.create_session()
        quiz = Questions()
        quiz.user_id = current_user.id
        quiz.topic = form.topic.data
        quiz.questions = str(form.question.data)
        quiz.subject = form.subject.data
        quiz.answers = form.answer.data
        db_sess.add(quiz)
        db_sess.commit()
        return redirect('/home')
    return render_template('quests.html', tit='Создание вопроса', form=form)

@app.route('/home/Change<int:id>', methods=['GET', 'POST'])
@login_required
def change_quiz(id):
    form = ChangeForm()
    if request.method == "GET":
        db_sess = sozdanie_BD.db_session.create_session()
        quest = db_sess.query(Questions).filter(Questions.id == id, Questions.user == current_user).first()
        if quest:
            form.topic.data = quest.topic
            form.subject.data = quest.subject
            form.answer.data = quest.answers
            form.question.data = quest.questions
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = sozdanie_BD.db_session.create_session()
        quest = db_sess.query(Questions).filter(Questions.id == id, Questions.user == current_user).first()

        if quest:
            quest.topic = form.topic.data
            quest.subject = form.subject.data
            quest.answers = form.answer.data
            quest.questions = form.question.data
            db_sess.commit()
            return redirect('/home')
        else:
            abort(404)

    return render_template('quests.html', form=form)

@app.route('/quizes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = sozdanie_BD.db_session.create_session()
    quest = db_sess.query(Questions).filter(Questions.id == id, Questions.user_id == current_user.id).first()
    if quest:
        db_sess.delete(quest)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/home')

@app.route('/Bot', methods=['GET'])
def Bot_page():
    return render_template('Bot.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangeInfo()
    if request.method == 'GET':
        db_sess = sozdanie_BD.db_session.create_session()
        userr = db_sess.query(Users).filter(Users.id == current_user.id).first()
        if userr:
            form.login.data = userr.login
            form.about.data = userr.about
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = sozdanie_BD.db_session.create_session()
        userr = db_sess.query(Users).filter(Users.id == current_user.id).first()

        if userr:
            userr.about = form.about.data
            userr.login = form.login.data
            db_sess.commit()
            return redirect('/home')
        else:
            abort(404)

    return render_template('profile.html', form=form)

@app.route('/')
def a():
    return render_template('base.html', title='Аунтефикация')

if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5000)