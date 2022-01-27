from asyncio import tasks
from crypt import methods
from distutils import text_file
from urllib import request, response
from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_sessionstore import Session

# app object
app = Flask(__name__)

# db uri config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#### added for creating a unique session
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'

db = SQLAlchemy(app)
session = Session(app)
session.app.session_interface.db.create_all()
####

# db template
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id column
    content = db.Column(db.String(500), nullable=False) # grocery list, 500 char max, can't be blank
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Lists {self.id}>'

# solution for heroku 500 Internal Error: https://stackoverflow.com/a/69814221
@app.before_first_request
def create_tables():
    db.create_all()

# main list
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        grocery_list = request.form['content']
        new_list = Todo(content=grocery_list)

        try:
            db.session.add(new_list)
            db.session.commit()
            return redirect('/')
        
        except:
            return "Unable to updated grocery list, try again!"

    else:
        lists = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", lists=lists)

# delete function
@app.route('/delete/<int:id>')
def delete(id):
    item_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect('/')
    
    except:
        return "Error: Unable to delete item from list"

# update function
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    list = Todo.query.get_or_404(id)

    if request.method == 'POST':
        list.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        
        except:
            return "Error: Issue with updating your item"
    else:
        return render_template('update.html', list=list)

if __name__ == "__main__":
    app.run(debug=True)