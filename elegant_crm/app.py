from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

# ===== قاعدة البيانات =====
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        with conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_number TEXT,
                    client_name TEXT,
                    gender TEXT,
                    governorate TEXT,
                    education TEXT,
                    marital_status TEXT,
                    has_children TEXT,
                    visa_type TEXT,
                    interest TEXT,
                    interest_level TEXT,
                    notes TEXT,
                    created_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS followups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_number TEXT,
                    client_name TEXT,
                    status TEXT,
                    notes TEXT,
                    followup_date TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_name TEXT,
                    client_phone TEXT,
                    appointment_date DATE,
                    created_at TIMESTAMP
                );
            ''')
        conn.close()

# ======= الصفحات =======

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO clients (employee_name, client_number, client_name, gender, governorate, education, marital_status,
            has_children, visa_type, interest, interest_level, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['employee_name'], data['client_number'], data['client_name'],
            data['gender'], data['governorate'], data['education'],
            data['marital_status'], data.get('has_children', ''),
            data['visa_type'], data['interest'], data.get('interest_level', ''),
            data.get('notes', ''), datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/contact')
    return render_template('contact_page.html')


@app.route('/view_followups', methods=['GET', 'POST'])
def view_followups():
    rows = []
    selected_employee = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM followups').fetchall()

    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        if selected_employee:
            rows = conn.execute('SELECT * FROM followups WHERE employee_name = ?', (selected_employee,)).fetchall()
    conn.close()

    return render_template('view_followups.html', rows=rows, employees=employees, selected_employee=selected_employee)


@app.route('/view_clients', methods=['GET', 'POST'])
def view_clients():
    rows = []
    selected_employee = ''
    searched_number = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM clients').fetchall()

    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        searched_number = request.form.get('client_number', '')

        if searched_number:
            rows = conn.execute('SELECT * FROM clients WHERE client_number = ?', (searched_number,)).fetchall()
        elif selected_employee:
            rows = conn.execute('SELECT * FROM clients WHERE employee_name = ?', (selected_employee,)).fetchall()
    conn.close()

    return render_template('view_clients.html', rows=rows, employees=employees,
                           selected_employee=selected_employee, searched_number=searched_number)


@app.route('/view_appointments', methods=['GET', 'POST'])
def view_appointments():
    rows = []
    selected_employee = ''
    selected_date = ''

    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM appointments').fetchall()

    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        selected_date = request.form.get('appointment_date', '')

        query = 'SELECT * FROM appointments WHERE 1=1'
        params = []

        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)

        if selected_date:
            query += ' AND appointment_date = ?'
            params.append(selected_date)

        rows = conn.execute(query, params).fetchall()

    conn.close()
    return render_template('view_appointments.html', rows=rows, employees=employees,
                           selected_employee=selected_employee, selected_date=selected_date)
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO appointments (employee_name, client_name, client_phone, appointment_date, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['employee_name'],
            data['client_name'],
            data['client_phone'],
            data['appointment_date'],
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/appointment')
    return render_template('appointment_page.html')
@app.route('/followup', methods=['GET', 'POST'])
def followup():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO followups (employee_name, client_number, client_name, status, notes, followup_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['employee_name'],
            data['client_number'],
            data['client_name'],
            data['status'],
            data.get('notes', ''),
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/followup')
    return render_template('followup_page.html')



# ======= تشغيل التطبيق =======
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
