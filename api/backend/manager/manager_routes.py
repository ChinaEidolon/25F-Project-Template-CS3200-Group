from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db
from mysql.connector import Error

# Setting up the blueprint for manager-specific routes
manager = Blueprint('manager', __name__)

# --- Helper: Validates and extracts date range from query params ---
def get_date_filters():
    """
    Tries to read start_date and end_date from query string.
    Returns tuple: (start_date, end_date, error_response or None)
    """
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    if not start or not end:
        # Return helpful error message if something's missing
        return None, None, (
            jsonify({
                "error": "Please provide both 'start_date' and 'end_date' in YYYY-MM-DD format."
            }),
            400
        )
    return start, end, None


# --- Endpoint: Revenue summary for the manager dashboard ---
@manager.route('/manager/revenue/summary', methods=['GET'])
def fetch_revenue_summary():
    try:
        start_date, end_date, error = get_date_filters()
        if error:
            return error

        current_app.logger.info(f"[SUMMARY] start={start_date}, end={end_date}")

        db_conn = db.get_db()
        cursor = db_conn.cursor()

        # Aggregating total and categorized revenues
        sql = """
            SELECT
                SUM(amount) AS total_billed,
                SUM(CASE WHEN status = 'paid'    THEN amount ELSE 0 END) AS paid_revenue,
                SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END) AS pending_revenue,
                SUM(CASE WHEN status = 'overdue' THEN amount ELSE 0 END) AS overdue_revenue
            FROM INVOICE
            WHERE service_date >= %s AND service_date < %s
        """

        current_app.logger.debug(f"Running revenue summary query with {start_date} to {end_date}")
        cursor.execute(sql, (start_date, end_date))
        row = cursor.fetchone()
        cursor.close()

        # If no data, default to zeros
        summary = {
            "total_billed":    row[0] or 0,
            "paid_revenue":    row[1] or 0,
            "pending_revenue": row[2] or 0,
            "overdue_revenue": row[3] or 0,
            "start_date":      start_date,
            "end_date":        end_date,
        }

        return jsonify(summary), 200

    except Error as err:
        current_app.logger.error(f"💥 DB error in revenue summary: {str(err)}")
        return jsonify({"error": str(err)}), 500


# --- Endpoint: Revenue grouped by each trainer ---
@manager.route('/manager/revenue/by-trainer', methods=['GET'])
def revenue_per_trainer():
    try:
        start_date, end_date, error = get_date_filters()
        if error:
            return error

        current_app.logger.info(f"[BY TRAINER] Revenue from {start_date} to {end_date}")

        cursor = db.get_db().cursor()

        sql = """
            SELECT
                t.trainer_id,
                t.first_name,
                t.last_name,
                SUM(i.amount) AS total_billed,
                SUM(CASE WHEN i.status = 'paid' THEN i.amount ELSE 0 END) AS paid_revenue
            FROM INVOICE i
            JOIN TRAINER t ON t.trainer_id = i.trainer_id
            WHERE i.service_date >= %s AND i.service_date < %s
            GROUP BY t.trainer_id, t.first_name, t.last_name
            ORDER BY paid_revenue DESC
        """

        cursor.execute(sql, (start_date, end_date))
        rows = cursor.fetchall()
        cursor.close()

        # Converting rows into dicts for JSON response
        trainer_revenue = []
        for r in rows:
            trainer_revenue.append({
                "trainer_id":   r[0],
                "first_name":   r[1],
                "last_name":    r[2],
                "total_billed": float(r[3] or 0),
                "paid_revenue": float(r[4] or 0),
            })

        return jsonify({
            "start_date": start_date,
            "end_date":   end_date,
            "trainers":   trainer_revenue
        }), 200

    except Error as err:
        current_app.logger.error(f"⚠️ DB error in revenue per trainer: {str(err)}")
        return jsonify({"error": str(err)}), 500


# --- Endpoint: Class revenue trend over time (optionally by trainer) ---
@manager.route('/manager/revenue/class-trend', methods=['GET'])
def class_revenue_over_time():
    try:
        start_date, end_date, error = get_date_filters()
        if error:
            return error

        trainer_id = request.args.get('trainer_id')  # Optional param
        current_app.logger.info(f"[TREND] start={start_date}, end={end_date}, trainer_id={trainer_id}")

        cursor = db.get_db().cursor()

        # Only include 'paid' invoices and filter on 'Class' category
        sql = """
            SELECT
                t.trainer_id,
                t.first_name,
                t.last_name,
                DATE(i.service_date) AS revenue_date,
                SUM(i.amount) AS total_revenue
            FROM INVOICE i
            JOIN TRAINER t ON t.trainer_id = i.trainer_id
            WHERE i.status = 'paid'
              AND i.category LIKE %s
              AND i.service_date >= %s
              AND i.service_date < %s
        """
        params = ['%Class%', start_date, end_date]

        if trainer_id:
            sql += " AND t.trainer_id = %s"
            params.append(trainer_id)

        sql += """
            GROUP BY
                t.trainer_id, t.first_name, t.last_name, DATE(i.service_date)
            ORDER BY
                revenue_date ASC, t.last_name ASC, t.first_name ASC
        """

        current_app.logger.debug(f"Class trend SQL: {sql} with {params}")
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()

        trend_data = []
        for r in rows:
            trend_data.append({
                "trainer_id":    r[0],
                "first_name":    r[1],
                "last_name":     r[2],
                "revenue_date":  r[3].isoformat() if hasattr(r[3], "isoformat") else str(r[3]),
                "total_revenue": float(r[4]) if r[4] else 0.0
            })

        return jsonify({
            "start_date": start_date,
            "end_date":   end_date,
            "trainer_id": trainer_id,
            "data":       trend_data
        }), 200

    except Error as err:
        current_app.logger.error(f"🚨 DB error in class trend: {str(err)}")
        return jsonify({"error": str(err)}), 500
