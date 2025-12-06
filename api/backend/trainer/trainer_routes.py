from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

# Create Blueprint
trainers = Blueprint('trainers', __name__)


# GET all trainers
@trainers.route('/trainers', methods=['GET'])
def get_all_trainers():
    try:
        current_app.logger.info('Starting get_all_trainers request')
        cursor = db.get_db().cursor()
        
        specialization = request.args.get('specialization')
        
        current_app.logger.debug(f'Query parameters - specialization: {specialization}')

        query = "SELECT * FROM trainer WHERE 1=1"
        params = []
        
        # Add filters
        if specialization:
            query += " AND specialization = %s"
            params.append(specialization)
        
        current_app.logger.debug(f'Executing query: {query} with params: {params}')
        cursor.execute(query, params)
        trainers_list = cursor.fetchall()
        cursor.close()
        
        current_app.logger.info(f'Successfully retrieved {len(trainers_list)} TRAINERS')
        return jsonify(trainers_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_trainers: {str(e)}')
        return jsonify({"error": str(e)}), 500

# GET specific trainer profile
@trainers.route('/trainers/<int:trainer_id>', methods=['GET'])
def get_trainer(trainer_id):
    try:
        cursor = db.get_db().cursor()

        # Get trainer details
        query = "SELECT * FROM trainer WHERE trainer_id = %s"
        cursor.execute(query, (trainer_id,))
        trainer = cursor.fetchone()
        
        if not trainer:
            return jsonify({"error": "Trainer not found"}), 404
        
        cursor.close()
        return jsonify(trainer), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new trainer
# Required fields: first_name, last_name
@trainers.route('/trainers', methods=['POST'])
def create_trainer():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["first_name", "last_name"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new trainer
        query = """
        INSERT INTO trainer (first_name, last_name, specialization)
        VALUES (%s, %s, %s)
        """
        cursor.execute(
            query,
            (
                data["first_name"],
                data["last_name"],
                data.get("specialization"),
            ),
        )
        
        db.get_db().commit()
        new_trainer_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Trainer created successfully", "trainer_id": new_trainer_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update trainer information
@trainers.route('/trainers/<int:trainer_id>', methods=['PUT'])
def update_trainer(trainer_id):
    try:
        data = request.get_json()
        
        # Check if trainer exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM trainer WHERE trainer_id = %s", (trainer_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Trainer not found"}), 404
        
        # Build update query based on fields
        update_fields = []
        params = []
        allowed_fields = ["first_name", "last_name", "specialization"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(trainer_id)
        query = f"UPDATE trainer SET {', '.join(update_fields)} WHERE trainer_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Trainer updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# GET all clients for a specific trainer
@trainers.route('/trainers/<int:trainer_id>/clients', methods=['GET'])
def get_trainer_clients(trainer_id):
    try:
        cursor = db.get_db().cursor()
        query = """
            SELECT member_id, first_name, last_name, email, status
            FROM gym_member
            WHERE trainer_id = %s
            ORDER BY last_name
        """
        cursor.execute(query, (trainer_id,))
        clients = cursor.fetchall()
        cursor.close()
        
        return jsonify(clients), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# GET specific client profile (for trainer view)
@trainers.route('/trainers/<int:trainer_id>/clients/<int:client_id>', methods=['GET'])
def get_client_profile(trainer_id, client_id):
    try:
        cursor = db.get_db().cursor()
        query = """
            SELECT gm.*, 
                   t.first_name as trainer_first_name, 
                   t.last_name as trainer_last_name
            FROM gym_member gm
            LEFT JOIN trainer t ON gm.trainer_id = t.trainer_id
            WHERE gm.member_id = %s AND gm.trainer_id = %s
        """
        cursor.execute(query, (client_id, trainer_id))
        client = cursor.fetchone()
        
        if not client:
            return jsonify({"error": "Client not found or not assigned to this trainer"}), 404
        
        cursor.close()
        return jsonify(client), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update client profile 
@trainers.route('/trainers/<int:trainer_id>/clients/<int:client_id>', methods=['PUT'])
def update_client_profile(trainer_id, client_id):
    try:
        data = request.get_json()
        
        # Verify client is assigned to this trainer
        cursor = db.get_db().cursor()
        cursor.execute(
            "SELECT * FROM gym_member WHERE member_id = %s AND trainer_id = %s", 
            (client_id, trainer_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Client not found or not assigned to this trainer"}), 404
        
        update_fields = []
        params = []
        allowed_fields = ["first_name", "last_name", "email", "status"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(client_id)
        query = f"UPDATE gym_member SET {', '.join(update_fields)} WHERE member_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Client profile updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# GET workout plans created by trainer
@trainers.route('/trainers/<int:trainer_id>/workout-plans', methods=['GET'])
def get_trainer_workout_plans(trainer_id):
    try:
        cursor = db.get_db().cursor()
        
        # Get member_id filter if provided
        member_id = request.args.get('member_id')
        
        query = """
            SELECT wp.*, gm.first_name, gm.last_name
            FROM workout_plan wp
            JOIN gym_member gm ON wp.member_id = gm.member_id
            WHERE gm.trainer_id = %s
        """
        params = [trainer_id]
        
        if member_id:
            query += " AND wp.member_id = %s"
            params.append(member_id)
        
        query += " ORDER BY wp.plan_date DESC"
        
        cursor.execute(query, params)
        plans = cursor.fetchall()
        cursor.close()
        
        return jsonify(plans), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create workout plan (User Story 2.2)
# Required fields: member_id, goals, plan_date
@trainers.route('/trainers/<int:trainer_id>/workout-plans', methods=['POST'])
def create_trainer_workout_plan(trainer_id):
    try:
        data = request.get_json()
        
        required_fields = ["member_id", "goals", "plan_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        cursor.execute(
            "SELECT * FROM gym_member WHERE member_id = %s AND trainer_id = %s",
            (data["member_id"], trainer_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Client not assigned to this trainer"}), 403
        
        # Insert new workout plan
        query = """
        INSERT INTO workout_plan (member_id, plan_name, goals, plan_date, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                data["member_id"],
                data.get("plan_name"),
                data["goals"],
                data["plan_date"],
                data.get("status", "active"),
            ),
        )
        
        db.get_db().commit()
        new_plan_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Workout plan created successfully", "plan_id": new_plan_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update workout plan
@trainers.route('/workout-plans/<int:plan_id>', methods=['PUT'])
def update_trainer_workout_plan(plan_id):
    try:
        data = request.get_json()
        
        # Check if workout plan exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM workout_plan WHERE plan_id = %s", (plan_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Workout plan not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["plan_name", "goals", "plan_date", "status"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(plan_id)
        query = f"UPDATE workout_plan SET {', '.join(update_fields)} WHERE plan_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Workout plan updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# GET workout logs for trainer's clients (User Story 2.3)
@trainers.route('/trainers/<int:trainer_id>/workout-logs', methods=['GET'])
def get_trainer_workout_logs(trainer_id):
    try:
        cursor = db.get_db().cursor()
        
        # Get member_id filter if provided
        member_id = request.args.get('member_id')
        
        query = """
            SELECT wl.*, gm.first_name, gm.last_name
            FROM workout_log wl
            JOIN gym_member gm ON wl.member_id = gm.member_id
            WHERE wl.trainer_id = %s
        """
        params = [trainer_id]
        
        if member_id:
            query += " AND wl.member_id = %s"
            params.append(member_id)
        
        query += " ORDER BY wl.workout_date DESC"
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        cursor.close()
        
        return jsonify(logs), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Record workout log (User Story 2.3)
@trainers.route('/trainers/<int:trainer_id>/workout-logs', methods=['POST'])
def create_trainer_workout_log(trainer_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["member_id", "workout_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Verify client is assigned to this trainer
        cursor = db.get_db().cursor()
        cursor.execute(
            "SELECT * FROM gym_member WHERE member_id = %s AND trainer_id = %s",
            (data["member_id"], trainer_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Client not assigned to this trainer"}), 403
        
        # Insert new workout log
        query = """
        INSERT INTO workout_log (member_id, trainer_id, workout_date, notes, sessions)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                data["member_id"],
                trainer_id,
                data["workout_date"],
                data.get("notes"),
                data.get("sessions", 1),
            ),
        )
        
        db.get_db().commit()
        new_log_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Workout log recorded successfully", "log_id": new_log_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update workout log notes (User Story 2.3)
@trainers.route('/workout-logs/<int:log_id>', methods=['PUT'])
def update_workout_log(log_id):
    try:
        data = request.get_json()
        
        # Check if workout log exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM workout_log WHERE log_id = %s", (log_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Workout log not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["notes", "sessions", "workout_date"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(log_id)
        query = f"UPDATE workout_log SET {', '.join(update_fields)} WHERE log_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Workout log updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE Delete workout log 
@trainers.route('/workout-logs/<int:log_id>', methods=['DELETE'])
def delete_workout_log(log_id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("DELETE FROM workout_log WHERE log_id = %s", (log_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Workout log deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# GET sessions for a trainer 
@trainers.route('/trainers/<int:trainer_id>/sessions', methods=['GET'])
def get_trainer_sessions(trainer_id):
    try:
        cursor = db.get_db().cursor()
        
        # Get date filter if provided
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = """
            SELECT cs.*, 
                   COUNT(ca.attendance_id) as enrolled_count
            FROM class_session cs
            LEFT JOIN class_attendance ca ON cs.session_id = ca.session_id
            WHERE cs.trainer_id = %s
        """
        params = [trainer_id]
        
        if date_from:
            query += " AND cs.session_date >= %s"
            params.append(date_from)
        if date_to:
            query += " AND cs.session_date <= %s"
            params.append(date_to)
        
        query += " GROUP BY cs.session_id ORDER BY cs.session_date DESC"
        
        cursor.execute(query, params)
        sessions = cursor.fetchall()
        cursor.close()
        
        return jsonify(sessions), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create session 
@trainers.route('/trainers/<int:trainer_id>/sessions', methods=['POST'])
def create_session(trainer_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["class_name", "session_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        query = """
        INSERT INTO class_session (trainer_id, class_name, session_date, cost)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                trainer_id,
                data["class_name"],
                data["session_date"],
                data.get("cost"),
            ),
        )
        
        db.get_db().commit()
        new_session_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Session created successfully", "session_id": new_session_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update session 
@trainers.route('/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    try:
        data = request.get_json()
        
        # Check if session exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM class_session WHERE session_id = %s", (session_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Session not found"}), 404
        
        update_fields = []
        params = []
        allowed_fields = ["class_name", "session_date", "cost"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(session_id)
        query = f"UPDATE class_session SET {', '.join(update_fields)} WHERE session_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Session updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Cancel session 
@trainers.route('/sessions/<int:session_id>', methods=['DELETE'])
def cancel_session(session_id):
    try:
        cursor = db.get_db().cursor()
        
        cursor.execute("DELETE FROM class_attendance WHERE session_id = %s", (session_id,))
        
        cursor.execute("DELETE FROM class_session WHERE session_id = %s", (session_id,))
        
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Session cancelled successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# GET invoices for trainer 
@trainers.route('/trainers/<int:trainer_id>/invoices', methods=['GET'])
def get_trainer_invoices(trainer_id):
    try:
        cursor = db.get_db().cursor()
        
        status = request.args.get('status')
        
        query = """
            SELECT i.*, gm.first_name, gm.last_name
            FROM invoice i
            JOIN gym_member gm ON i.member_id = gm.member_id
            WHERE i.trainer_id = %s
        """
        params = [trainer_id]
        
        if status:
            query += " AND i.status = %s"
            params.append(status)
        
        query += " ORDER BY i.invoice_date DESC"
        
        cursor.execute(query, params)
        invoices = cursor.fetchall()
        cursor.close()
        
        return jsonify(invoices), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Create invoice 
@trainers.route('/trainers/<int:trainer_id>/invoices', methods=['POST'])
def create_invoice(trainer_id):
    try:
        data = request.get_json()
        
        # Validate reuired fields
        required_fields = ["member_id", "amount", "invoice_date", "category"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        query = """
        INSERT INTO invoice (member_id, trainer_id, amount, invoice_date, status, category)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                data["member_id"],
                trainer_id,
                data["amount"],
                data["invoice_date"],
                data.get("status", "pending"),
                data["category"],
            ),
        )
        
        db.get_db().commit()
        new_invoice_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Invoice created successfully", "invoice_id": new_invoice_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update invoice status 
@trainers.route('/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    try:
        data = request.get_json()
        
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM invoice WHERE invoice_id = %s", (invoice_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Invoice not found"}), 404
        
        update_fields = []
        params = []
        allowed_fields = ["status", "amount", "category"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(invoice_id)
        query = f"UPDATE invoice SET {', '.join(update_fields)} WHERE invoice_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Invoice updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Cancel invoice 
@trainers.route('/invoices/<int:invoice_id>', methods=['DELETE'])
def void_invoice(invoice_id):
    try:
        cursor = db.get_db().cursor()
        
        cursor.execute(
            "UPDATE invoice SET status = 'voided' WHERE invoice_id = %s", 
            (invoice_id,)
        )
        
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Invoice voided successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# GET messages between trainer and clients (User Story 2.6)
@trainers.route('/trainers/<int:trainer_id>/messages', methods=['GET'])
def get_trainer_messages(trainer_id):
    try:
        cursor = db.get_db().cursor()
        
        # Get member_id filter if provided
        member_id = request.args.get('member_id')
        
        query = """
            SELECT m.*, gm.first_name, gm.last_name
            FROM message m
            JOIN gym_member gm ON m.member_id = gm.member_id
            WHERE m.trainer_id = %s
        """
        params = [trainer_id]
        
        if member_id:
            query += " AND m.member_id = %s"
            params.append(member_id)
        
        query += " ORDER BY m.message_timestamp DESC"
        
        cursor.execute(query, params)
        messages = cursor.fetchall()
        cursor.close()
        
        return jsonify(messages), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Send message to client 
@trainers.route('/trainers/<int:trainer_id>/messages', methods=['POST'])
def send_trainer_message(trainer_id):
    try:
        data = request.get_json()
        
        required_fields = ["member_id", "content"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        query = """
        INSERT INTO message (member_id, trainer_id, content, message_timestamp, read_status)
        VALUES (%s, %s, %s, NOW(), %s)
        """
        cursor.execute(
            query,
            (
                data["member_id"],
                trainer_id,
                data["content"],
                data.get("read_status", "unread"),
            ),
        )
        
        db.get_db().commit()
        new_message_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Message sent successfully", "message_id": new_message_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500