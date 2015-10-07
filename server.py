import sqlite3
from flask import Flask, request, session, g, url_for, render_template, jsonify

# configuration
DATABASE = './db.sqlite'
DEBUG = True

# Changing default jinja delimiters because of conflict with Angular's
class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update({
        'variable_start_string': '%%',
        'variable_end_string': '%%'
    })

app = CustomFlask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()




class Persons:
    COLUMNS = ['id', 'first_name', 'last_name', 'telephone']

    class Person:
        def __init__(self, id, first_name, last_name, telephone):
            self.id = id
            self.first_name = first_name
            self.last_name = last_name
            self.telephone = telephone

        def serialize(self):
            return {
                'id': self.id, 
                'first_name': self.first_name,
                'last_name': self.last_name,
                'telephone': self.telephone,
            }

        def __str__(self):
            return str(self.id) + ': ' + self.first_name + ' ' + self.last_name


    def filter(self, page, sort, order, query):
        try:
            page = int(page)
        except ValueError:
            page = 1

        if page < 1:
            page = 1

        offset = str((page - 1) * 10)

        if sort not in self.COLUMNS:
            sort = self.COLUMNS[0]

        query = '%' + query + '%'
        order = 'DESC' if order == 'desc' else 'ASC'

        sql = 'SELECT * FROM data WHERE (id LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR telephone LIKE ?)'

        cur = g.db.cursor()
        cur.execute(sql, (query, query, query, query))
        totalPersons = len(cur.fetchall())

        cur.execute(sql + ' ORDER BY ' + sort + ' ' + order + ' LIMIT 10 OFFSET ' + offset, (query, query, query, query))
        persons = [self.Person(row[0], row[1], row[2], row[3]).serialize() for row in cur.fetchall()]

        return { 'persons': persons, 'totalItems': totalPersons }



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/persons')
def get_persons():
    page = request.args.get('page', 1)
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    query = request.args.get('query', '')

    persons = Persons()
    return jsonify(persons.filter(page, sort, order, query))
   



if __name__ == '__main__':
    app.run(host = '0.0.0.0')