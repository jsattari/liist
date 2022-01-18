from asyncio import tasks
from urllib import request
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# app object
app = Flask(__name__)

# db uri config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# db template
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id column
    content = db.Column(db.String(500), nullable=False) # grocery list, 500 char max, can't be blank
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Lists {self.id}>'

# page paths
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
    item_to_delte = Todo.query.get_or_404(id)

    try:
        db.session.delete(item_to_delte)
        db.session.commit()
        return redirect('/')
    
    except:
        return "Error: Unable to delete item from list"


if __name__ == "__main__":
    app.run(debug=True)