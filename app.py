from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Ad, Question, Purchase, FavoriteList

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
        conn.commit()
        self.id = cursor.lastrowid
        conn.close()

    def create_ad(self, category_id, title, description, price):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO ads (user_id, category_id, title, description, price) VALUES (?, ?, ?, ?, ?)',
                       (self.id, category_id, title, description, price))
        conn.commit()
        conn.close()

    def ask_question(self, ad_id, question):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO questions (ad_id, user_id, question) VALUES (?, ?, ?)', (ad_id, self.id, question))
        conn.commit()
        conn.close()

    def answer_question(self, question_id, answer):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE questions SET answer = ? WHERE id = ? AND (SELECT user_id FROM ads WHERE id = ad_id) = ?',
                       (answer, question_id, self.id))
        conn.commit()
        conn.close()

    def make_purchase(self, ad_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO purchases (ad_id, buyer_id, purchase_date) VALUES (?, ?, ?)',
                       (ad_id, self.id, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def add_to_favorites(self, ad_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO favorite_lists (user_id, ad_id) VALUES (?, ?)', (self.id, ad_id))
        conn.commit()
        conn.close()

    def get_sales_report(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ads WHERE user_id = ?', (self.id,))
        sales = cursor.fetchall()
        conn.close()
        return sales

    def get_purchases_report(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM purchases WHERE buyer_id = ?', (self.id,))
        purchases = cursor.fetchall()
        conn.close()
        return purchases

class Category:
    def __init__(self, name):
        self.name = name
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        conn.commit()
        self.id = cursor.lastrowid
        conn.close()

class Ad:
    def __init__(self, user_id, category_id, title, description, price):
        self.user_id = user_id
        self.category_id = category_id
        self.title = title
        self.description = description
        self.price = price
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO ads (user_id, category_id, title, description, price) VALUES (?, ?, ?, ?, ?)',
                       (user_id, category_id, title, description, price))
        conn.commit()
        self.id = cursor.lastrowid
        conn.close()

class Question:
    def __init__(self, ad_id, user_id, question, answer=None):
        self.ad_id = ad_id
        self.user_id = user_id
        self.question = question
        self.answer = answer
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO questions (ad_id, user_id, question, answer) VALUES (?, ?, ?, ?)',
                       (ad_id, user_id, question, answer))
        conn.commit()
        self.id = cursor.lastrowid
        conn.close()

class Purchase:
    def __init__(self, ad_id, buyer_id):
        self.ad_id = ad_id
        self.buyer_id = buyer_id
        self.purchase_date = datetime.now().isoformat()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO purchases (ad_id, buyer_id, purchase_date) VALUES (?, ?, ?)',
                       (ad_id, buyer_id, self.purchase_date))
        conn.commit()
        self.id = cursor.lastrowid
        conn.close()

class FavoriteList:
    def __init__(self, user_id, ad_id):
        self.user_id = user_id
        self.ad_id = ad_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO favorite_lists (user_id, ad_id) VALUES (?, ?)', (user_id, ad_id))
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ads')
    ads = cursor.fetchall()
    conn.close()
    return render_template('index.html', ads=ads)

@app.route('/ad/<int:ad_id>')
def ad_detail(ad_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ads WHERE id = ?', (ad_id,))
    ad = cursor.fetchone()
    cursor.execute('SELECT * FROM questions WHERE ad_id = ?', (ad_id,))
    questions = cursor.fetchall()
    conn.close()
    return render_template('ad_detail.html', ad=ad, questions=questions)

@app.route('/user/<int:user_id>/sales')
def sales_report(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ads WHERE user_id = ?', (user_id,))
    sales = cursor.fetchall()
    conn.close()
    return render_template('sales_report.html', sales=sales)

@app.route('/user/<int:user_id>/purchases')
def purchases_report(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM purchases WHERE buyer_id = ?', (user_id,))
    purchases = cursor.fetchall()
    conn.close()
    return render_template('purchases_report.html', purchases=purchases)

@app.route('/create_ad', methods=['GET', 'POST'])
def create_ad():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category_id']
        user_id = session['user_id']
        
        new_ad = Ad(title=title, description=description, price=price, category_id=category_id, user_id=user_id)
        db.session.add(new_ad)
        db.session.commit()
        
        return redirect(url_for('user_dashboard'))
    return render_template('create_ad.html')

@app.route('/ads')
def list_ads():
    ads = Ad.query.all()
    return render_template('ads.html', ads=ads)

@app.route('/ad/<int:ad_id>')
def view_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return render_template('view_ad.html', ad=ad)

@app.route('/ads')
def list_ads():
    ads = Ad.query.all()
    return render_template('ads.html', ads=ads)

@app.route('/ad/<int:ad_id>')
def view_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return render_template('view_ad.html', ad=ad)

@app.route('/edit_ad/<int:ad_id>', methods=['GET', 'POST'])
def edit_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    if request.method == 'POST':
        ad.title = request.form['title']
        ad.description = request.form['description']
        ad.price = request.form['price']
        db.session.commit()
        return redirect(url_for('view_ad', ad_id=ad_id))
    return render_template('edit_ad.html', ad=ad)

@app.route('/delete_ad/<int:ad_id>', methods=['POST'])
def delete_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

    @app.route('/create_ad', methods=['GET', 'POST'])
def create_ad():
    if 'user_id' not in session:
        return redirect(url_for('login')) 
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category_id']
        user_id = session['user_id']
        
        new_ad = Ad(title=title, description=description, price=price, category_id=category_id, user_id=user_id)
        db.session.add(new_ad)
        db.session.commit()
        
        return redirect(url_for('user_dashboard'))
    return render_template('create_ad.html')

@app.route('/edit_ad/<int:ad_id>', methods=['GET', 'POST'])
def edit_ad(ad_id):
    if 'user_id' not in session:
        return redirect(url_for('login')) 
    ad = Ad.query.get_or_404(ad_id)
    if request.method == 'POST':
        ad.title = request.form['title']
        ad.description = request.form['description']
        ad.price = request.form['price']
        db.session.commit()
        return redirect(url_for('view_ad', ad_id=ad_id))
    return render_template('edit_ad.html', ad=ad)

@app.route('/delete_ad/<int:ad_id>', methods=['POST'])
def delete_ad(ad_id):
    if 'user_id' not in session:
        return redirect(url_for('login')) 
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/user/<int:user_id>/sales')
def sales_report(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ads WHERE user_id = ?', (user_id,))
    sales = cursor.fetchall()
    conn.close()
    return render_template('sales_report.html', sales=sales)

@app.route('/user/<int:user_id>/purchases')
def purchases_report(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM purchases WHERE buyer_id = ?', (user_id,))
    purchases = cursor.fetchall()
    conn.close()
    return render_template('purchases_report.html', purchases=purchases)
