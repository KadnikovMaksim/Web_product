from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class CreateForm(FlaskForm):
    topic = StringField('Тема', validators=[DataRequired()])
    subject = StringField('Предмет', validators=[DataRequired()])
    question = StringField("Вопрос", validators=[DataRequired()])
    answer = StringField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Создать')

class ChangeForm(FlaskForm):
    topic = StringField('Тема', validators=[DataRequired()])
    subject = StringField('Предмет', validators=[DataRequired()])
    question = StringField("Вопрос", validators=[DataRequired()])
    answer = StringField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Сохранить')