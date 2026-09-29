from flask import Flask, render_template, request, redirect, session
from functools import wraps 
import sqlite3
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.secret_key = "streamline-hr-development-key"

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

def get_current_user():
    user_id = session.get("user_id", 1)

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM employees WHERE employee_id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    return user

def hr_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()

        if user is None or user["role"] != "hr":
            return "Access denied. HR role required.", 403

        return view_function(*args, **kwargs)

    return wrapped_view

def validate_leave_request(
    employee,
    leave_type,
    start_date,
    end_date
):
    allowed_leave_types = [
        "Annual Leave",
        "Sick Leave",
        "Unpaid Leave"
    ]

    if leave_type not in allowed_leave_types:
        return "Please select a valid leave type.", None

    if end_date < start_date:
        return "End date cannot be before start date.", None

    if start_date < date.today().isoformat():
        return "Leave cannot start before today's date.", None

    working_days = calculate_working_days(
        start_date,
        end_date
    )

    if (
        leave_type == "Annual Leave"
        and working_days > employee["leave_balance"]
    ):
        return (
            f"Insufficient leave balance. "
            f"You have {employee['leave_balance']} days available.",
            None
        )

    return None, working_days

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
            
            employee = connection.execute(
                "SELECT * FROM employees WHERE employee_id = 1"
            ).fetchone()
            
            connection.close()
            
            validation_error, working_days = validate_leave_request(
                employee,
                leave_type,
                start_date,
                end_date
            )
            
            if validation_error:
                message = validation_error
            
            else:
                connection = get_db_connection()
            
                overlapping_request = connection.execute("""
                    SELECT *
                    FROM leave_requests
                    WHERE employee_id = ?
                      AND status IN ('Pending', 'Approved')
                      AND NOT (end_date < ? OR start_date > ?)
                """, (
                    1,
                    start_date,
                    end_date
                )).fetchone()
            
                if overlapping_request:
                    message = (
                        "This leave request overlaps with an existing "
                        "pending or approved request."
                    )
            
                    connection.close()
            
                else:
                    reason = request.form["reason"]
            
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

@app.route("/switch-user/<int:user_id>")
def switch_user(user_id):
    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM employees WHERE employee_id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    if user is None:
        return "User not found", 404

    session["user_id"] = user_id

    if user["role"] == "hr":
        return redirect("/hr")

    return redirect("/")

@app.route("/hr")
@hr_required
def hr_dashboard():   
    connection = get_db_connection()

    pending_requests = connection.execute("""
        SELECT
            leave_requests.*,
            employees.name AS employee_name
        FROM leave_requests
        JOIN employees
            ON leave_requests.employee_id = employees.employee_id
        WHERE leave_requests.status = 'Pending'
        ORDER BY leave_requests.created_at ASC
    """).fetchall()

    connection.close()

    return render_template(
        "hr_dashboard.html",
        pending_requests=pending_requests
    )


@app.route("/hr/request/<int:request_id>/<action>", methods=["POST"])
@hr_required
def update_leave_request(request_id, action):
    if action not in ["approve", "reject"]:
        return "Invalid action", 400

    connection = get_db_connection()

    leave_request_record = connection.execute("""
        SELECT *
        FROM leave_requests
        WHERE request_id = ?
    """, (request_id,)).fetchone()

    if leave_request_record is None:
        connection.close()
        return "Leave request not found", 404

    if leave_request_record["status"] != "Pending":
        connection.close()
        return "Leave request has already been processed", 400

    if action == "approve":
        new_status = "Approved"
        
        if leave_request_record["leave_type"] == "Annual Leave":
                connection.execute("""
                    UPDATE employees
                    SET leave_balance = leave_balance - ?
                    WHERE employee_id = ?
                """, (
                    leave_request_record["working_days"],
                    leave_request_record["employee_id"]
                ))

    else:
        new_status = "Rejected"


    connection.execute("""
        UPDATE leave_requests
        SET status = ?
        WHERE request_id = ?
    """, (
        new_status,
        request_id
    ))    

    connection.commit()
    connection.close()

    return redirect("/hr")

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
