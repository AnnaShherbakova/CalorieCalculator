from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, FloatField, IntegerField, HiddenField
from wtforms.validators import *

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    birthday = DateField('birthday', validators=[DataRequired()])
    sex = SelectField('sex', choices=[('f', 'Женский'), ('m', 'Мужской')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AddParams(FlaskForm):
    user_weight = IntegerField('Вес', validators=[DataRequired()])
    user_growth = IntegerField('Рост', validators=[DataRequired()])
    calorie = IntegerField('Калории', validators=[DataRequired()])
    proteins = IntegerField('Протеины', validators=[DataRequired()])
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
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    birthday = DateField('birthday', validators=[DataRequired()])
    sex = SelectField('sex', choices=[('f', 'Женский'), ('m', 'Мужской')])
    submit = SubmitField('Sign In')