from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Function to initialize database
def init_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='formdata'
    )
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), email VARCHAR(50), password VARCHAR(50))''')
    c.execute('''CREATE TABLE IF NOT EXISTS ticketinfo
                 (id INT AUTO_INCREMENT PRIMARY KEY, full_name VARCHAR(50), email VARCHAR(50), mobile_number VARCHAR(20), age INT, ticket_price INT, picture VARCHAR(255))''')
    conn.commit()
    conn.close()

# Define a function to fetch past tickets data
def fetch_past_tickets():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='formdata'
    )
    c = conn.cursor()
    c.execute("SELECT * FROM ticketinfo")
    past_tickets = c.fetchall()
    conn.close()
    return past_tickets

# Landing page
@app.route('/')
def homepage():
    # Redirect to index.html
    return redirect(url_for('index'))

# Index route
@app.route('/index')
def index():
    # You can add any logic you want to display on the index page here
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='formdata'
        )
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            # Authentication successful, redirect to homepage
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            # Authentication failed, display error message
            flash('Invalid email or password', 'error')
            return render_template('login.html')
    return render_template('login.html')

# Homepage route
@app.route('/home')
def home():
    # You can add any logic you want to display on the homepage here
    return render_template('home.html')

@app.route('/contact')
def contact():
    # You can add any logic you want to display on the homepage here
    return render_template('contact.html')
# About route
@app.route('/about')
def about():
    return render_template('about.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='formdata'
        )
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        conn.close()
        # Redirect to login page after successful signup
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Buy tickets route
@app.route('/buy_tickets', methods=['GET', 'POST'])
def buy_tickets():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        age = request.form['age']
        ticket_price = request.form['ticket_price']
        picture = request.files['picture']

        # Ensure the 'uploads' directory exists
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        # Save the picture to the 'uploads' folder
        picture_path = os.path.join(uploads_dir, picture.filename)
        picture.save(picture_path)

        # Save data and image path to the database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='formdata'
        )
        c = conn.cursor()
        c.execute("INSERT INTO ticketinfo (full_name, email, mobile_number, age, ticket_price, picture) VALUES (%s, %s, %s, %s, %s, %s)", (full_name, email, mobile_number, age, ticket_price, picture_path))
        conn.commit()
        conn.close()

        # Redirect to thank you page
        return redirect(url_for('thank_you'))

    return render_template('buy_tickets.html')

# Thank you page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# History route
@app.route('/history')
def history():
    past_tickets = fetch_past_tickets()
    return render_template('history.html', past_tickets=past_tickets)

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
