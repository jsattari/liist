from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# app object
app = Flask(__name__)

# db uri config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# 
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id column
    content = db.Column(db.String(500), nullable=False) # grocery list, 500 char max, can't be blank
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

# page paths
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)