from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                matric TEXT NOT NULL,
                receipt_path TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def home():
    return redirect(url_for('submit'))

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form.get('name')
        matric = request.form.get('matric')
        file = request.files.get('receipt')

        if not name or not matric or not file:
            return "<h3 style='color:red;'>Please fill in all fields and upload your receipt.</h3>"

        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute(
                'INSERT INTO submissions (name, matric, receipt_path) VALUES (?, ?, ?)',
                (name, matric, filepath)
            )
            conn.commit()

        return "<h3 style='color:teal;'>✅ Submission successful! You can now close this page.</h3>"

    return render_template('submit.html')

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT name, matric, receipt_path FROM submissions ORDER BY id DESC')
        data = c.fetchall()
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
