import os
import json
import random
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, RadioField
from wtforms.validators import InputRequired
from flask import Flask, render_template, request

# Импортируем данные для передачи их в шаблон
import data

class BookingForm(FlaskForm):
    name = StringField('name', [InputRequired()])
    phone = StringField('phone', [InputRequired()])
    time = HiddenField('time')
    day = HiddenField('day')

class RequestForm(FlaskForm):
    lesson = RadioField('lesson',  choices=[('1', 'Для путешествий'), ('2', 'Для школы'), ('3', 'Для работы'), ('4','Для переезда')])
    time_has = RadioField('time_has',  choices=[('1', '1-2 часа в неделю'),('2','3-5 часов в неделю'),('3', '5-7 часов в неделю'),('4','7-10 часов в неделю')])
    name = StringField('name', [InputRequired()])
    phone = StringField('phone', [InputRequired()])


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/')
def index():
    teachers = []
    for i in range(0,6):
        teachers.append(random.choice(data.teachers))
    return render_template('index.html', teachers=teachers)


@app.route('/goal/<type>')
def goal(type):
    teachers = []
    for v in data.teachers:
        if type in v['goals']:
            teachers.append(v)

    return render_template('goal.html', teachers=teachers, goal=data.goals[type])


@app.route('/profile/<int:id>')
def profile(id):
    # формируем данные о преподавателе
    goals = []
    for t in data.teachers:
        if t['id'] == id:
            teacher = t
            for g in t['goals']:
                goals.append(data.goals[g])
            return render_template('profile.html', teacher=teacher, goals=goals)
    return 'Преподаватель не найден'


@app.route('/booking/<int:id>/<day>/<int:time>')
def booking(id, day, time):
    for t in data.teachers:
        if t['id'] == id:
            teacher = t
            break

    form = BookingForm(time=time, day=day)

    return render_template('booking.html',
                           teacher=teacher,
                           time=time,
                           weekday=data.weekday[day],
                           form=form)

@app.route('/booking_done', methods=["GET","POST"])
def booking_done():
    form = BookingForm()
    # Обновляем json файл с заявками
    if request.method == 'POST':
        append_dict = {
            'name': form.name.data,
            'phone': form.phone.data,
            'time': form.time.data,
            'day': data.weekday[form.day.data]
        }

        insert_dict = {}
        key = hash(str(form.name.data)+'\\'+str(form.phone.data)+'\\'+str(form.time.data)+'\\'+str(data.weekday[form.day.data]))
        insert_dict[key] = append_dict

        with open('booking.json') as f:
            book = json.load(f)
        book.update(insert_dict)

        with open('booking.json', 'w') as f:
            json.dump(book, f)
        return render_template('booking_done.html', append_dict=append_dict)
    else:
        return 'Ошибка'

@app.route('/request')
def request_action():
    form = RequestForm()
    return render_template('request.html', form=form)

@app.route('/request_done', methods=["GET","POST"])
def request_done():
    form = RequestForm()
    if request.method == 'POST':
        value = form.lesson.data
        choices = dict(form.lesson.choices)
        lesson = choices[value]

        value = form.time_has.data
        choices = dict(form.time_has.choices)
        time_has = choices[value]

        append_dict = {
            'name': form.name.data,
            'phone': form.phone.data,
            'lesson': lesson,
            'time_has': time_has
        }


        insert_dict = {}
        key = hash(str(form.name.data)+'\\'+str(form.phone.data)+'\\'+str(lesson)+'\\'+str(time_has))
        insert_dict[key] = append_dict

        with open('request.json') as f:
            req = json.load(f)
        req.update(insert_dict)
        with open('request.json', 'w') as f:
            json.dump(req, f)

        return render_template('request_done.html', append_dict=append_dict)
    else:
        return 'Ошибка'

if __name__ == '__main__':
    app.run('0.0.0.0',7000)
