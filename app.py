import hashlib
from datetime import datetime
from xmlrpc.client import DateTime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, redirect, url_for, flash, session, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import models, forms
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger, swag_from

from config import app, db, migrate, login

Swagger(app)

@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@app.route('/logout')
@swag_from('api/logout_get.yml', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@swag_from('api/index_get.yml', methods=['GET'])
def index():
    return render_template('index.html', title='Main')


@app.route('/register', methods=['get', 'post'])
@swag_from('api/register_get.yml', methods=['GET'])
@swag_from('api/register_post.yml', methods=['POST'])
def register():
    form = forms.RegisterForm()
    if form.is_submitted():
        u = models.User(username=form.username.data, email=form.email.data, birthday=form.birthday.data,
                        sex=form.sex.data, password_hash=generate_password_hash(form.password.data))
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
@swag_from('api/login_get.yml', methods=['GET'])
@swag_from('api/login_post.yml', methods=['POST'])
def login():
    form = forms.LoginForm()
    if form.is_submitted():
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
@swag_from('api/dishes_get.yml', methods=['GET'])
@swag_from('api/dishes_post.yml', methods=['POST'])
def dishes():
    f = forms.AddDishes()
    if f.is_submitted() and session['admin']:
        p = models.Dishes(name=f.name.data, calorie=f.calorie.data, proteins=f.proteins.data, fats=f.fats.data,
                          carbohydrates=f.carbohydrates.data)
        db.session.add(p)
        db.session.commit()
    d = models.Dishes.query.all()
    return render_template('dishes.html', title='Dishes', form=f, dishes=d)


@app.route('/admin_deaut')
@swag_from('api/admin_deaut_get.yml', methods=['GET'])
def admin_deaut():
    session['admin'] = False
    return '<script>document.location.href = document.referrer</script>'


@app.route('/delete_meals', methods=["POST"])
@swag_from('api/delete_meals_post.yml', methods=['POST'])
def meals_delete():
    f = forms.DeleteMeals()
    if f.is_submitted():
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
        return '<script>document.location.href = document.referrer</script>'
        #return redirect('cabinet_' + str(current_user.id))


@app.route('/param', methods=["POST"])
@login_required
@swag_from('api/param_post.yml', methods=['POST'])
def param():
    f = forms.AddParams()
    if f.is_submitted():
        p = models.Parametrs(user_id=current_user.id, user_weight=f.user_weight.data, user_growth=f.user_growth.data,
                             calorie=f.calorie.data, proteins=f.proteins.data, fats=f.fats.data,
                             carbohydrates=f.carbohydrates.data)
        db.session.add(p)
        db.session.commit()
        return '<script>document.location.href = document.referrer</script>'
        #return redirect('cabinet_' + str(current_user.id))


@app.route('/meals', methods=["POST"])
@login_required
@swag_from('api/meals_post.yml', methods=['POST'])
def meals():
    f = forms.AddMeals([])
    f.dishes.choices = [(str(i.id), i.name) for i in models.Dishes.query.all()]

    if f.is_submitted():
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
        return '<script>document.location.href = document.referrer</script>'
        #return redirect('cabinet_' + str(current_user.id))


@app.route('/change_user', methods=['POST'])
@login_required
@swag_from('api/change_user_post.yml', methods=['POST'])
def change_user():
    f = forms.ChangeUser()
    if f.is_submitted():
        u = models.User.query.filter_by(id=current_user.id).first()
        u.password_hash = generate_password_hash(f.password.data)
        u.sex = f.sex.data
        u.birthday = f.birthday.data
        u.email = f.email.data
        db.session.commit()
        return '<script>document.location.href = document.referrer</script>'
        #return redirect('cabinet_' + str(current_user.id))


def calculator(sex, weight, height, age, target):
    Calorie = 0
    proteins = 0
    fats = 0
    carbohydrates = 0

    if sex == 'm':
        Calorie = 88.36 + 13.4 * weight + 4.8 * height - 5.7 * age
        if target == 1:
            Calorie += 200
        elif target == -1:
            Calorie -= 200
    else:
        Calorie = 447.6 + 9.2 * weight + 3.1 * height - 4.3 * age
        if target == 1:
            Calorie += 200
        elif target == -1:
            Calorie -= 200

    proteins = (0.4 * Calorie) / 4
    fats = (0.25 * Calorie) / 9
    carbohydrates = (0.35 * Calorie) / 4
    return Calorie, proteins, fats, carbohydrates


@app.route('/calc', methods=['POST'])
@login_required
@swag_from('api/calc_post.yml', methods=['POST'])
def calc():
    koef = request.form['koef']
    ss = models.Parametrs.query.filter_by(user_id=current_user.id).order_by(models.Parametrs.datetime.desc()).first()
    Calorie, proteins, fats, carbohydrates = calculator(current_user.sex, ss.user_weight, ss.user_growth,
                                                        relativedelta(datetime.today() - current_user.birthday).years,
                                                        int(koef))
    return jsonify({'calorie': Calorie, 'proteins': proteins, 'fats': fats, 'carbohydrates': carbohydrates})


@app.route('/cabinet_<user_id>')
@login_required
@swag_from('api/cabinet_.yml', methods=['GET'])
def cabinet(user_id):
    u = models.User.query.filter_by(id=user_id).first()
    f4 = forms.ChangeUser()

    return render_template('cabinet.html', username=u.username, email=u.email, birthday=u.birthday, sex=u.sex,
                           title='Кабинет пользователя', meals=meals, form4=f4)


@app.route('/journal')
@login_required
@swag_from('api/journal_get.yml', methods=['GET'])
def journal():
    p = models.Parametrs.query.filter_by(user_id=current_user.id)
    date_from = None
    date_to = None
    if 'date_from' in request.args and request.args['date_from'] != '':
        date_from = datetime.strptime(request.args['date_from'], '%Y-%m-%d')
        p = p.filter(models.Parametrs.datetime >= date_from)
    if 'date_to' in request.args and request.args['date_to'] != '':
        date_to = datetime.strptime(request.args['date_to'], '%Y-%m-%d')
        p = p.filter(models.Parametrs.datetime <= date_to)

    p = p.all()

    if date_from is not None:
        date_from = date_from.strftime('%Y-%m-%d')
    else:
        date_from = ''

    if date_to is not None:
        date_from = date_to.strftime('%Y-%m-%d')
    else:
        date_to = ''
    f = forms.AddParams()

    return render_template('journal.html', title='Дневник', params=p, form=f, day_from=date_from, day_to=date_to)


@app.route('/user_meals')
@login_required
@swag_from('api/user_meals_get.yml', methods=['GET'])
def user_meals():
    date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, hour=0, minute=0,
                    second=0, microsecond=0)
    f2 = forms.AddMeals([])
    f2.dishes.choices = [(str(i.id), i.name) for i in models.Dishes.query.all()]
    f3 = forms.DeleteMeals()
    meals = models.Meals.query.filter(models.Daily_intake.date >= date).filter_by(user_id=current_user.id).all()
    food = {i.id: i.name for i in models.Dishes.query.all()}
    return render_template('meals.html', title='Приемы пищи', form2=f2, food=food, form3=f3, meals=meals)


@app.route('/statistics')
@login_required
@swag_from('api/statistics_get.yml', methods=['GET'])
def statistics():
    q = models.Daily_intake.query.filter_by(user_id=current_user.id)
    date_from = None
    date_to = None
    if 'date_from' in request.args and request.args['date_from'] != '':
        date_from = datetime.strptime(request.args['date_from'], '%Y-%m-%d')
        q = q.filter(models.Daily_intake.date >= date_from)
    if 'date_to' in request.args and request.args['date_to'] != '':
        date_to = datetime.strptime(request.args['date_to'], '%Y-%m-%d')
        q = q.filter(models.Daily_intake.date <= date_to)

    daily = q.all()

    if date_from is not None:
        date_from = date_from.strftime('%Y-%m-%d')
    else:
        date_from = ''

    if date_to is not None:
        date_from = date_to.strftime('%Y-%m-%d')
    else:
        date_to = ''

    return render_template('statistics.html', title='Статистика', daily=daily, day_from=date_from, day_to=date_to)


if __name__ == '__main__':
    app.run(debug=True)
