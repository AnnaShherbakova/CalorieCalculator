from datetime import datetime

from flask_login import UserMixin

from config import db

class User(UserMixin, db.Model): #пользователи
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    birthday = db.Column(db.DateTime)
    sex = db.Column(db.String(16))

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Admins(UserMixin, db.Model): #админы
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<Admin {}>'.format(self.id)

class Dishes(db.Model): #Блюда
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    calorie = db.Column(db.Integer)
    proteins = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)

    def __repr__(self):
        return '<Dishes {}>'.format(self.username)

class Daily_intake(db.Model): #Суточная доза
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    calorie = db.Column(db.Integer)
    proteins = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)

    def __repr__(self):
        return '<Daily_intake {}>'.format(self.username)

class Parametrs(db.Model): #Параметры
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    user_weight = db.Column(db.Integer)
    user_growth = db.Column(db.Integer)
    calorie = db.Column(db.Integer)
    proteins = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)
    def __repr__(self):
        return '<Parametrs {}>'.format(self.username)

class Meals(db.Model): #Еда
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dishes_id = db.Column(db.Integer, db.ForeignKey('dishes.id'))
    dishes_weight = db.Column(db.Integer)
    calorie = db.Column(db.Integer)
    proteins = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)
    def __repr__(self):
        return '<Meals {}>'.format(self.username)
