"""OpenAQ Air Quality Dashboard with Flask"""
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from openaq_py import OpenAQ


# Create app and DataBase
APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


# Table for database to store retrieved data
class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'<Time {self.datetime} --- Value {self.value}>'


def get_utc_values(city, parameter):
    """
    Function for pulling in data from api
    Returns tuple of datetime and value"""
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


# Route to home page
@APP.route('/')
def root():
    """Base View."""
    if not DB.engine.dialect.has_table(DB.engine, 'record'):
        DB.create_all()
        records = []
        return render_template('home.html', records=records)
    else:
        records = Record.query.filter(Record.value >= 10).all()
        return render_template('home.html', records=records)


# route to refresh page for cleaning and reestablishing just LA in db
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
