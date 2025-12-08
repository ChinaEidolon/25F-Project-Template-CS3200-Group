from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import db
from mysql.connector import Error

managers = Blueprint('managers', __name__)

# --- Helper: grabs date range from query params ---
def parse_date_range():
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    if not start or not end:
        return None, None, (
            jsonify({"error": "Missing required 'start_date' and 'end_date' query parameters (format: YYYY-MM-DD)"}),
            400
        )
    return start, end, None


# --- Revenue Summary: Basic dashboard totals ---
@managers.route('/revenue/summary', methods=['GET'])
def revenue_summary():
    try:
        start, end, error = parse_date_range()
        if error:
            return error

        current_app.logger.info(f"[SUMMARY] Fetching revenue from {start} to {end}")

        conn = db.get_db()
        cur = conn.cursor()

        # Simple total & status breakdown
        query = """
            SELECT
                SUM(amount) AS total,
                SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) AS paid,
                SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'overdue' THEN amount ELSE 0 END) AS overdue
            FROM INVOICE
            WHERE date >= %s AND date < %s
        """

        cur.execute(query, (start, end))
        result = cur.fetchone()
        cur.close()

        # Build response with fallback zeros
        response = {
            "total_billed":    result['total'] or 0 if result else 0,
            "paid_revenue":    result['paid'] or 0 if result else 0,
            "pending_revenue": result['pending'] or 0 if result else 0,
            "overdue_revenue": result['overdue'] or 0 if result else 0,
            "start_date":      start,
            "end_date":        end
        }

        return jsonify(response), 200

    except Error as e:
        current_app.logger.error(f"[DB ERROR] Revenue summary blew up: {str(e)}")
        return jsonify({"error": "Something went wrong fetching revenue summary."}), 500


# --- Trainer Revenue: Lists revenue per trainer ---
@managers.route('/revenue/by-trainer', methods=['GET'])
def trainer_revenue():
    try:
        start, end, error = parse_date_range()
        if error:
            return error

        current_app.logger.info(f"[BY TRAINER] Pulling data from {start} to {end}")

        db_conn = db.get_db()
        cursor = db_conn.cursor()

        sql = """
            SELECT
                t.trainer_id,
                t.first_name,
                t.last_name,
                SUM(i.amount) AS total_billed,
                SUM(CASE WHEN i.status = 'paid' THEN i.amount ELSE 0 END) AS paid_revenue
            FROM INVOICE i
            JOIN TRAINER t ON t.trainer_id = i.trainer_id
            WHERE i.date >= %s AND i.date < %s
            GROUP BY t.trainer_id, t.first_name, t.last_name
            ORDER BY paid_revenue DESC
        """

        cursor.execute(sql, (start, end))
        rows = cursor.fetchall()
        cursor.close()

        data = []
        for row in rows:
            data.append({
                "trainer_id":   row['trainer_id'],
                "first_name":   row['first_name'],
                "last_name":    row['last_name'],
                "total_billed": float(row['total_billed'] or 0),
                "paid_revenue": float(row['paid_revenue'] or 0)
            })

        return jsonify({
            "start_date": start,
            "end_date": end,
            "trainers": data
        }), 200

    except Error as err:
        current_app.logger.error(f"[DB ERROR] Could not fetch trainer revenue: {str(err)}")
        return jsonify({"error": "Trainer revenue query failed"}), 500


@managers.route('/revenue/class-trend', methods=['GET'])
def revenue_trend_by_class():
    try:
        start, end, error = parse_date_range()
        if error:
            return error

        tid = request.args.get('trainer_id')

        current_app.logger.info(f"[TREND] Date range: {start} to {end} | Trainer: {tid}")

        conn = db.get_db()
        cur = conn.cursor()

        query = """
            SELECT
                t.trainer_id,
                t.first_name,
                t.last_name,
                DATE(i.date) AS revenue_date,
                SUM(i.amount) AS total_revenue
            FROM INVOICE i
            JOIN TRAINER t ON t.trainer_id = i.trainer_id
            WHERE i.status = 'paid'
              AND i.category LIKE %s
              AND i.date >= %s AND i.date < %s
        """
        params = ['%Class%', start, end]

        if tid:
            query += " AND t.trainer_id = %s"
            params.append(tid)

        query += """
            GROUP BY t.trainer_id, t.first_name, t.last_name, DATE(i.date)
            ORDER BY revenue_date ASC, t.last_name ASC
        """

        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()

        trend = []
        for r in rows:
            trend.append({
                "trainer_id": r['trainer_id'],
                "first_name": r['first_name'],
                "last_name": r['last_name'],
                "revenue_date": r['revenue_date'].isoformat() if hasattr(r['revenue_date'], "isoformat") else str(r['revenue_date']),
                "total_revenue": float(r['total_revenue']) if r['total_revenue'] else 0.0
            })

        return jsonify({
            "start_date": start,
            "end_date": end,
            "trainer_id": tid,
            "data": trend
        }), 200

    except Error as db_err:
        current_app.logger.error(f"Trend query failed: {str(db_err)}")
        return jsonify({"error": "Failed to retrieve revenue trend data"}), 500


# --- Attendance: Class attendance logs ---
@managers.route('/class-attendance', methods=['GET'])
def attendance_log():
    try:
        trainer = request.args.get('trainer_id')
        start = request.args.get('start_date')
        end = request.args.get('end_date')

        current_app.logger.info(f"[ATTENDANCE] Filtering by trainer={trainer}, from={start}, to={end}")

        conn = db.get_db()
        cur = conn.cursor()

        sql = """
            SELECT
                ca.attendance_id,
                ca.session_id,
                ca.member_id,
                ca.status,
                cs.class_name,
                cs.date AS class_datetime,
                cs.cost,
                cs.trainer_id,
                t.first_name AS trainer_first_name,
                t.last_name AS trainer_last_name,
                gm.first_name AS member_first_name,
                gm.last_name AS member_last_name
            FROM CLASS_ATTENDANCE ca
            JOIN CLASS_SESSION cs ON ca.session_id = cs.session_id
            JOIN TRAINER t ON cs.trainer_id = t.trainer_id
            JOIN GYM_MEMBER gm ON ca.member_id = gm.member_id
            WHERE 1=1
        """
        params = []

        if trainer:
            sql += " AND cs.trainer_id = %s"
            params.append(trainer)

        if start and end:
            sql += " AND cs.date BETWEEN %s AND %s"
            params.extend([start, end])

        sql += " ORDER BY cs.date DESC, cs.class_name ASC"

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()

        attendance = []
        for entry in rows:
            attendance.append({
                "attendance_id": entry['attendance_id'],
                "session_id": entry['session_id'],
                "member_id": entry['member_id'],
                "status": entry['status'],
                "class_name": entry['class_name'],
                "class_datetime": entry['class_datetime'].isoformat() if hasattr(entry['class_datetime'], 'isoformat') else str(entry['class_datetime']),
                "cost": float(entry['cost'] or 0.0),
                "trainer_id": entry['trainer_id'],
                "trainer_name": f"{entry['trainer_first_name']} {entry['trainer_last_name']}",
                "member_name": f"{entry['member_first_name']} {entry['member_last_name']}"
            })

        return jsonify(attendance), 200

    except Error as e:
        current_app.logger.error(f"[DB ERROR] Attendance data error: {str(e)}")
        return jsonify({"error": "Could not get class attendance"}), 500


# --- Revenue by Category: Analyze different revenue streams ---
@managers.route('/revenue/by-category', methods=['GET'])
def revenue_by_category():
    try:
        start, end, error = parse_date_range()
        if error:
            return error

        current_app.logger.info(f"[CATEGORY] Revenue breakdown from {start} to {end}")

        cur = db.get_db().cursor()

        sql = """
            SELECT
                DATE(date) AS revenue_date,
                category,
                SUM(amount) AS total_revenue,
                SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) AS paid_revenue
            FROM INVOICE
            WHERE date >= %s AND date < %s
              AND category IS NOT NULL
            GROUP BY DATE(date), category
            ORDER BY revenue_date ASC, category ASC
        """

        cur.execute(sql, (start, end))
        rows = cur.fetchall()
        cur.close()

        category_results = []
        for row in rows:
            category_results.append({
                "revenue_date": row['revenue_date'].isoformat() if hasattr(row['revenue_date'], 'isoformat') else str(row['revenue_date']),
                "category": row['category'],
                "total_revenue": float(row['total_revenue'] or 0),
                "paid_revenue": float(row['paid_revenue'] or 0)
            })

        return jsonify({
            "start_date": start,
            "end_date": end,
            "data": category_results
        }), 200

    except Error as err:
        current_app.logger.error(f"[ERROR] Category revenue query failed: {str(err)}")
        return jsonify({"error": "Couldn’t fetch revenue breakdown"}), 500
