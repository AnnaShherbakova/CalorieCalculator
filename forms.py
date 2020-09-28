from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, FloatField, IntegerField, HiddenField
from wtforms.validators import *

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    birthday = DateField('Дата рождения', validators=[DataRequired()])
    sex = SelectField('Пол', choices=[('f', 'Женский'), ('m', 'Мужской')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')

class AddParams(FlaskForm):
    user_weight = IntegerField('Вес', validators=[DataRequired()])
    user_growth = IntegerField('Рост', validators=[DataRequired()])
    calorie = IntegerField('Калории', validators=[DataRequired()])
    proteins = IntegerField('Белки', validators=[DataRequired()])
    fats = IntegerField('Жиры', validators=[DataRequired()])
    carbohydrates = IntegerField('Углеводы', validators=[DataRequired()])
    submit = SubmitField('Добавить запись')

class AddDishes(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    calorie = IntegerField('Калории', validators=[DataRequired()])
    proteins = IntegerField('Белки', validators=[DataRequired()])
    fats = IntegerField('Жиры', validators=[DataRequired()])
    carbohydrates = IntegerField('Углеводы', validators=[DataRequired()])
    submit = SubmitField('Добавить продукт')

class AddMeals(FlaskForm):
    dishes = SelectField('Продукт', validators=[DataRequired()])
    def __init__(self, meals):
        super().__init__()
        AddMeals.dishes = SelectField('Продукт', validators=[DataRequired()], choices=meals)
    dishes_weight = IntegerField('Вес продукта', validators=[DataRequired()])
    submit = SubmitField('Добавить порцию')

class DeleteMeals(FlaskForm):
    id = HiddenField('id')
    submit = SubmitField('Удалить')

class ChangeUser(FlaskForm):
    id = HiddenField('id')
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    birthday = DateField('Дата рождения', validators=[DataRequired()])
    sex = SelectField('Пол', choices=[('f', 'Женский'), ('m', 'Мужской')])
    submit = SubmitField('Изменить')

