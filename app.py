import hashlib
from datetime import datetime
from xmlrpc.client import DateTime

from flask import Flask, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import models, forms
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import app, db, migrate, login


@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html', title='Main')


@app.route('/register', methods=['get', 'post'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        u = models.User(username=form.username.data, email=form.email.data, birthday=form.birthday.data,
                        sex=form.sex.data, password_hash=generate_password_hash(form.password.data))
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        if form.username.data != 'admin':
            user = models.User.query.filter_by(username=form.username.data).first()
            if user is None or not user.password_hash != generate_password_hash(form.password.data):
                flash('Неправильный логин или пароль')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            session['admin'] = False
            return redirect('cabinet_' + str(user.id))
        else:
            admin = models.Admins.query.filter_by(password_hash=form.password.data).first()
            if admin is not None:
                session['admin'] = True
                return redirect(url_for('dishes'))
            else:
                flash('Неправильный логин или пароль')
                return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)


@app.route('/dishes', methods=["GET", "POST"])
def dishes():
    f = forms.AddDishes()
    if f.validate_on_submit() and session['admin']:
        p = models.Dishes(name=f.name.data, calorie=f.calorie.data, proteins=f.proteins.data, fats=f.fats.data,
                          carbohydrates=f.carbohydrates.data)
        db.session.add(p)
        db.session.commit()
    d = models.Dishes.query.all()
    return render_template('dishes.html', title='Dishes', form=f, dishes=d)

@app.route('/admin_deaut')
def admin_deaut():
    session['admin'] = False
    return '<script>document.location.href = document.referrer</script>'


@app.route('/delete_meals', methods=["POST"])
def meals_delete():
    f = forms.DeleteMeals()
    if f.validate_on_submit():
        p = models.Meals.query.filter_by(id=f.id.data).first()
        date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, hour=0, minute=0,
                        second=0, microsecond=0)
        daily = models.Daily_intake.query.filter(
            models.Daily_intake.date >= date).filter_by(user_id=current_user.id).first()

        daily.calorie -= p.calorie
        daily.proteins -= p.proteins
        daily.fats -= p.fats
        daily.carbohydrates -= p.carbohydrates

        p = models.Meals.query.filter_by(id=f.id.data).delete()
        db.session.commit()
        return redirect('cabinet_' + str(current_user.id))


@app.route('/param', methods=["POST"])
@login_required
def param():
    f = forms.AddParams()
    if f.validate_on_submit():
        p = models.Parametrs(user_id=current_user.id, user_weight=f.user_weight.data, user_growth=f.user_growth.data,
                             calorie=f.calorie.data, proteins=f.proteins.data, fats=f.fats.data,
                             carbohydrates=f.carbohydrates.data)
        db.session.add(p)
        db.session.commit()
        return redirect('cabinet_' + str(current_user.id))


@app.route('/meals', methods=["POST"])
@login_required
def meals():
    f = forms.AddMeals([])
    f.dishes.choices = [(str(i.id), i.name) for i in models.Dishes.query.all()]

    if f.validate_on_submit():
        d = models.Dishes.query.filter_by(id=f.dishes.data).first()
        p = models.Meals(user_id=current_user.id, dishes_id=int(f.dishes.data),
                         dishes_weight=f.dishes_weight.data,
                         calorie=int(d.calorie * float(f.dishes_weight.data) / 100),
                         proteins=int(d.proteins * float(f.dishes_weight.data) / 100),
                         fats=int(d.fats * float(f.dishes_weight.data) / 100),
                         carbohydrates=int(d.carbohydrates * float(f.dishes_weight.data) / 100))
        date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, hour=0, minute=0,
                        second=0, microsecond=0)
        daily = models.Daily_intake.query.filter(
            models.Daily_intake.date >= date).filter_by(user_id=current_user.id).first()
        if daily is None:
            daily = models.Daily_intake(user_id=current_user.id, calorie=p.calorie, proteins=p.proteins, fats=p.fats,
                                        carbohydrates=p.carbohydrates)
            db.session.add(daily)
        else:
            daily.calorie += p.calorie
            daily.proteins += p.proteins
            daily.fats += p.fats
            daily.carbohydrates += p.carbohydrates

        db.session.add(p)
        db.session.commit()
        return redirect('cabinet_' + str(current_user.id))

@app.route('/change_user', methods=['POST'])
@login_required
def change_user():
    f = forms.ChangeUser()
    if f.validate_on_submit():
        u = models.User.query.filter_by(id=current_user.id).first()
        u.password_hash = generate_password_hash(f.password.data)
        u.sex = f.sex.data
        u.birthday = f.birthday.data
        u.email = f.email.data
        db.session.commit()
        return redirect('cabinet_' + str(current_user.id))

@app.route('/cabinet_<user_id>')
@login_required
def cabinet(user_id):
    u = models.User.query.filter_by(id=user_id).first()
    f = forms.AddParams()
    f2 = forms.AddMeals([])
    f3 = forms.DeleteMeals()
    f4 = forms.ChangeUser()
    f2.dishes.choices = [(str(i.id), i.name) for i in models.Dishes.query.all()]
    p = models.Parametrs.query.filter_by(user_id=current_user.id).all()
    daily = models.Daily_intake.query.all()
    date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, hour=0, minute=0,
                    second=0, microsecond=0)
    meals = models.Meals.query.filter(
        models.Daily_intake.date >= date).filter_by(user_id=current_user.id).all()
    food = {i.id: i.name for i in models.Dishes.query.all()}
    return render_template('cabinet.html', username=u.username, email=u.email, birthday=u.birthday, sex=u.sex, form2=f2,
                           form=f,
                           title='Кабинет пользователя', params=p, daily=daily, meals=meals, food=food, form3=f3,
                           form4=f4)


if __name__ == '__main__':
    app.run()
