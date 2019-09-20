"""OpenAQ Air Quality Dashboard with Flask"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from openaq_py import OpenAQ

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'<Time {self.datetime} --- Value {self.value}>'


def get_utc_values(city, parameter):
    api = OpenAQ()
    status, body = api.measurements(city=city, parameter=parameter)
    datetimes = []
    values = []
    for result in body['results']:
        datetime = result['date']['utc']
        value = result['value']
        datetimes.append(datetime)
        values.append(value)
    records = list(zip(datetimes, values))
    return records


@APP.route('/')
def root():
    """Base View."""
    records = Record.query.filter(Record.value >= 10).all()
    return render_template('home.html', records=records)


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data"""
    DB.drop_all()
    DB.create_all()
    # TODO get data from OpenAQ make Record objects with it and add to db
    records = get_utc_values('Los Angeles', 'pm25')
    for tup in records:
        record = Record(datetime=tup[0], value=tup[1])
        DB.session.add(record)
        DB.session.commit()
    return 'Data refreshed!'
