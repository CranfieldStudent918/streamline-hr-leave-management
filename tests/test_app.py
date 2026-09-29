# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 16:57:54 2026

@author: firda
"""
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app import app, calculate_working_days, validate_leave_request


def test_calculate_working_days():
    assert calculate_working_days("2026-10-05", "2026-10-09") == 5


def test_end_date_before_start_date():
    employee = {
        "leave_balance": 25
    }

    message, working_days = validate_leave_request(
        employee,
        "Annual Leave",
        "2026-10-10",
        "2026-10-05"
    )

    assert message == "End date cannot be before start date."
    assert working_days is None


def test_invalid_leave_type():
    employee = {
        "leave_balance": 25
    }

    message, working_days = validate_leave_request(
        employee,
        "Holiday",
        "2026-10-05",
        "2026-10-09"
    )

    assert message == "Please select a valid leave type."
    assert working_days is None


def test_insufficient_annual_leave_balance():
    employee = {
        "leave_balance": 2
    }

    message, working_days = validate_leave_request(
        employee,
        "Annual Leave",
        "2026-10-05",
        "2026-10-09"
    )

    assert "Insufficient leave balance" in message
    assert working_days is None


def test_valid_leave_request():
    employee = {
        "leave_balance": 25
    }

    message, working_days = validate_leave_request(
        employee,
        "Annual Leave",
        "2026-10-05",
        "2026-10-09"
    )

    assert message is None
    assert working_days == 5
    
from datetime import date, timedelta


def test_exact_annual_leave_balance_is_allowed():
    employee = {
        "leave_balance": 5
    }

    message, working_days = validate_leave_request(
        employee,
        "Annual Leave",
        "2026-10-05",
        "2026-10-09"
    )

    assert message is None
    assert working_days == 5


def test_past_start_date_is_rejected():
    employee = {
        "leave_balance": 25
    }

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    message, working_days = validate_leave_request(
        employee,
        "Annual Leave",
        yesterday,
        tomorrow
    )

    assert message == "Leave cannot start before today's date."
    assert working_days is None


def test_employee_cannot_access_hr_dashboard():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = 1

        response = client.get("/hr")

        assert response.status_code == 403
        assert b"HR role required" in response.data


def test_hr_user_can_access_hr_dashboard():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = 2

        response = client.get("/hr")

        assert response.status_code == 200
        assert b"HR Leave Management" in response.data

def test_invalid_hr_action_is_rejected():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = 2

        response = client.post("/hr/request/1/delete")

        assert response.status_code == 400
        assert b"Invalid action" in response.data


def test_employee_cannot_process_leave_request():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = 1

        response = client.post("/hr/request/1/approve")

        assert response.status_code == 403
        assert b"HR role required" in response.data