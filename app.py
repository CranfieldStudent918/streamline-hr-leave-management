from flask import Flask, render_template, request
import sqlite3
from datetime import date, datetime, timedelta

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect("streamline_hr.db")
    connection.row_factory = sqlite3.Row
    return connection


def calculate_working_days(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    working_days = 0
    current_date = start

    while current_date <= end:
        if current_date.weekday() < 5:
            working_days += 1

        current_date += timedelta(days=1)

    return working_days


def create_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            leave_balance INTEGER NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            working_days INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (employee_id)
                REFERENCES employees (employee_id)
        )
    """)

    connection.execute("""
        INSERT OR IGNORE INTO employees
        (employee_id, name, email, role, leave_balance)
        VALUES
        (1, 'Alex Morgan', 'alex.morgan@streamlinecorp.com', 'employee', 25)
    """)

    connection.execute("""
        INSERT OR IGNORE INTO employees
        (employee_id, name, email, role, leave_balance)
        VALUES
        (2, 'Sam Taylor', 'sam.taylor@streamlinecorp.com', 'hr', 0)
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    connection = get_db_connection()

    employee = connection.execute(
        "SELECT * FROM employees WHERE employee_id = 1"
    ).fetchone()

    leave_requests = connection.execute("""
        SELECT *
        FROM leave_requests
        WHERE employee_id = 1
        ORDER BY created_at DESC
    """).fetchall()
    
    connection.close()

    return render_template(
        "dashboard.html",
        employee=employee,
        leave_requests=leave_requests
    )


@app.route("/leave-request", methods=["GET", "POST"])
def leave_request():
    message = None

    if request.method == "POST":
        leave_type = request.form["leave_type"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        allowed_leave_types = [
            "Annual Leave",
            "Sick Leave",
            "Unpaid Leave"
        ]

        if leave_type not in allowed_leave_types:
            message = "Please select a valid leave type."

        elif end_date < start_date:
            message = "End date cannot be before start date."

        elif start_date < date.today().isoformat():
            message = "Leave cannot start before today's date."

        else:
            working_days = calculate_working_days(start_date, end_date)

            connection = get_db_connection()

            employee = connection.execute(
                "SELECT * FROM employees WHERE employee_id = 1"
            ).fetchone()

            connection.close()

            if (
                 leave_type == "Annual Leave"
                 and working_days > employee["leave_balance"]
              ):
                 message = (
                     f"Insufficient leave balance. "
                     f"You have {employee['leave_balance']} days available."
                 )

            else:
                reason = request.form["reason"]
                    
                connection = get_db_connection()
                connection.execute("""
                     INSERT INTO leave_requests
                     (
                           employee_id,
                           leave_type,
                           start_date,
                           end_date,
                           working_days,
                           status,
                           reason,
                           created_at                         
                      )
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               """, (
                   1,
                   leave_type,
                   start_date,
                   end_date,
                   working_days,
                   "Pending",
                   reason,
                   datetime.now().isoformat()
            ))

            connection.commit()
            connection.close()

            message = (
                f"Leave request submitted successfully. "
                f"Working days requested: {working_days}. "
                f"Status: Pending."
            )  
                     
    return render_template(
        "leave request.html",
        message=message
    )


if __name__ == "__main__":
    create_database()
    app.run(debug=True)