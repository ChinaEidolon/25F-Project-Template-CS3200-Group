from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

# Create Blueprint
members = Blueprint('members', __name__)

# GET all members (filtered by status, trainer, or nutritionist)
@members.route('/members', methods=['GET'])
def get_all_members():
    try:
        print("error check in member_routes.py")
        current_app.logger.info('Starting get_all_members request')
        cursor = db.get_db().cursor()
        
        # Get query parameters for filtering
        status = request.args.get('status')
        trainer_id = request.args.get('trainer_id')
        nutritionist_id = request.args.get('nutritionist_id')
        
        current_app.logger.debug(f'Query parameters - status: {status}, trainer_id: {trainer_id}, nutritionist_id: {nutritionist_id}')

        # Prepare the Base query
        query = "SELECT * FROM GYM_MEMBER WHERE 1=1"
        params = []
        
        # Add filters
        if status:
            query += " AND status = %s"
            params.append(status)
        if trainer_id:
            query += " AND trainer_id = %s"
            params.append(trainer_id)
        if nutritionist_id:
            query += " AND nutritionist_id = %s"
            params.append(nutritionist_id)
        
        current_app.logger.debug(f'Executing query: {query} with params: {params}')
        cursor.execute(query, params)
        members = cursor.fetchall()
        cursor.close()
        
        current_app.logger.info(f'Successfully retrieved {len(members)} MEMBERS')
        return jsonify(members), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_members: {str(e)}')
        return jsonify({"error": str(e)}), 500

# GET specific member profile
@members.route('/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        cursor = db.get_db().cursor()

        # Get member details
        query = "SELECT * FROM GYM WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        member = cursor.fetchone()
        
        if not member:
            return jsonify({"error": "Member not found"}), 404
        
        cursor.close()
        return jsonify(member), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
# POST - Create new member
# Required fields: first_name, last_name, email
# Optional: trainer_id, nutritionist_id, status
@members.route('/members', methods=['POST'])
def create_member():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["first_name", "last_name"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new member
        query = """
        INSERT INTO GYM_MEMBER (first_name, last_name, email, trainer_id, nutritionist_id, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                data["first_name"],
                data["last_name"],
                data["email"],
                data.get("trainer_id"),
                data.get("nutritionist_id"),
                data.get("status", "active"),
            ),
        )
        
        db.get_db().commit()
        new_member_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Member created successfully", "member_id": new_member_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Update an existing member's information
# Can update any field except member_id
@members.route('/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    try:
        data = request.get_json()
        
        # Check if member exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM GYM_MEMBER WHERE member_id = %s", (member_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Member not found"}), 404
        
        # Build update query based on fields
        update_fields = []
        params = []
        allowed_fields = ["first_name", "last_name", "email", "trainer_id", "nutritionist_id", "status"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(member_id)
        query = f"UPDATE GYM_MEMBER SET {', '.join(update_fields)} WHERE member_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Member updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Deactivate member (soft delete)
@members.route('/<int:member_id>', methods=['DELETE'])
def deactivate_member(member_id):
    try:
        cursor = db.get_db().cursor()
        query = "UPDATE GYM_MEMBER SET status = 'cancelled' WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Member deactivated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# GOALS commands
# GET all goals for a member
@members.route('/<int:member_id>/goals', methods=['GET'])
def get_member_goals(member_id):
    try:
        cursor = db.get_db().cursor()
        query = "SELECT * FROM goal WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        goals = cursor.fetchall()
        cursor.close()
        
        return jsonify(goals), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new goal
# Required fields: goal_type, target_value
@members.route('/<int:member_id>/goals', methods=['POST'])
def create_goal(member_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["goal_type", "target_value"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new goal
        query = """
        INSERT INTO goal (member_id, goal_type, target_value, current_value, deadline)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                member_id,
                data["goal_type"],
                data["target_value"],
                data.get("current_value"),
                data.get("deadline"),
            ),
        )
        
        db.get_db().commit()
        new_goal_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Goal created successfully", "goal_id": new_goal_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update goal
@members.route('/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    try:
        data = request.get_json()
        
        # Check if goal exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM goal WHERE goal_id = %s", (goal_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Goal not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["target_value", "current_value", "deadline", "goal_type"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(goal_id)
        query = f"UPDATE goal SET {', '.join(update_fields)} WHERE goal_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Goal updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Delete goal
@members.route('/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("DELETE FROM goal WHERE goal_id = %s", (goal_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Goal deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# WORKOUT LOGS commands
# GET workout logs for a member
@members.route('/<int:member_id>/workout-logs', methods=['GET'])
def get_workout_logs(member_id):
    try:
        cursor = db.get_db().cursor()
        query = """
            SELECT * FROM WORKOUT_LOG
            WHERE member_id = %s 
            ORDER BY date DESC
        """
        cursor.execute(query, (member_id,))
        logs = cursor.fetchall()
        cursor.close()
        
        return jsonify(logs), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Log new workout
# Required fields: workout_date
@members.route('/<int:member_id>/workout-logs', methods=['POST'])
def create_workout_log(member_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["workout_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new workout log
        query = """
        INSERT INTO WORKOUT_LOG (member_id, trainer_id, date, notes, sessions)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                member_id,
                data.get("trainer_id"),
                data["workout_date"],
                data.get("notes"),
                data.get("sessions", 1),
            ),
        )
        
        db.get_db().commit()
        new_log_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Workout logged successfully", "log_id": new_log_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500


# PROGRESS commands
# GET progress for a member
@members.route('/<int:member_id>/progress', methods=['GET'])
def get_progress(member_id):
    try:
        cursor = db.get_db().cursor()
        query = """
            SELECT * FROM PROGRESS 
            WHERE member_id = %s 
            ORDER BY date DESC
        """
        cursor.execute(query, (member_id,))
        progress = cursor.fetchall()
        cursor.close()
        
        return jsonify(progress), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new progress entry
# Required fields: progress_date
@members.route('/<int:member_id>/progress', methods=['POST'])
def create_progress(member_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["progress_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new progress entry
        query = """
        INSERT INTO PROGRESS (member_id, date, weight, body_fat_percentage, measurements, photos)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                member_id,
                data.get("progress_date"),
                data.get("weight"),
                data.get("body_fat_percentage"),
                data.get("measurements"),
                data.get("photos"),
            ),
        )
        
        db.get_db().commit()
        new_progress_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Progress recorded successfully", "progress_id": new_progress_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update progress entry
@members.route('/progress/<int:progress_id>', methods=['PUT'])
def update_progress(progress_id):
    try:
        data = request.get_json()
        
        # Check if progress entry exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM PROGRESS WHERE progress_id = %s", (progress_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Progress entry not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["weight", "body_fat_percentage", "measurements", "photos"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(progress_id)
        query = f"UPDATE PROGRESS SET {', '.join(update_fields)} WHERE progress_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Progress updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Delete progress entry
@members.route('/progress/<int:progress_id>', methods=['DELETE'])
def delete_progress(progress_id):
    try:
        cursor = db.get_db().cursor()
        query = "DELETE FROM PROGRESS WHERE progress_id = %s"
        cursor.execute(query, (progress_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Progress entry deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
# WORKOUT PLANS commands
# GET workout plans for a member
@members.route('/<int:member_id>/workout-plans', methods=['GET'])
def get_workout_plans(member_id):
    try:
        cursor = db.get_db().cursor()
        query = "SELECT * FROM WORKOUT_PLAN WHERE member_id = %s ORDER BY date DESC"
        cursor.execute(query, (member_id,))
        plans = cursor.fetchall()
        cursor.close()
        
        return jsonify(plans), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# GET specific workout plan details
@members.route('/workout-plans/<int:plan_id>', methods=['GET'])
def get_workout_plan(plan_id):
    try:
        cursor = db.get_db().cursor()
        query = "SELECT * FROM WORKOUT_PLAN WHERE plan_id = %s"
        cursor.execute(query, (plan_id,))
        plan = cursor.fetchone()
        cursor.close()
        
        if not plan:
            return jsonify({"error": "Workout plan not found"}), 404
        
        return jsonify(plan), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new workout plan
# Required fields: plan_date
@members.route('/<int:member_id>/workout-plans', methods=['POST'])
def create_workout_plan(member_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["goals", "plan_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new workout plan
        query = """
        INSERT INTO WORKOUT_PLAN (member_id, goals, date)
        VALUES (%s, %s, %s)
        """
        cursor.execute(
            query,
            (
                member_id,
                data["goals"],
                data.get("plan_date"), 
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
@members.route('/workout-plans/<int:plan_id>', methods=['PUT'])
def update_workout_plan(plan_id):
    try:
        data = request.get_json()
        
        # Check if workout plan exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM WORKOUT_PLAN WHERE plan_id = %s", (plan_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Workout plan not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["plan_date", "goals", "plan_name", "status"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(plan_id)
        query = f"UPDATE WORKOUT_PLAN SET {', '.join(update_fields)} WHERE plan_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Workout plan updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# MESSAGES commands
# GET messages for a member
@members.route('/<int:member_id>/messages', methods=['GET'])
def get_member_messages(member_id):
    try:
        cursor = db.get_db().cursor()
        query = """
            SELECT m.*, t.first_name as trainer_first_name, t.last_name as trainer_last_name
            FROM MESSAGE m
            LEFT JOIN TRAINER t ON m.trainer_id = t.trainer_id
            WHERE m.member_id = %s
            ORDER BY m.message_timestamp DESC
        """
        cursor.execute(query, (member_id,))
        messages = cursor.fetchall()
        cursor.close()
        
        return jsonify(messages), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# GET specific message
@members.route('/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    try:
        cursor = db.get_db().cursor()
        query = "SELECT * FROM message WHERE message_id = %s"
        cursor.execute(query, (message_id,))
        message = cursor.fetchone()
        cursor.close()
        
        if not message:
            return jsonify({"error": "Message not found"}), 404
        
        return jsonify(message), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Send new message
# Required fields: content
@members.route('/<int:member_id>/messages', methods=['POST'])
def create_message(member_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["content"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new message
        query = """
        INSERT INTO MESSAGE (member_id, trainer_id, content, message_timestamp, read_status)
        VALUES (%s, %s, %s, NOW(), %s)
        """
        cursor.execute(
            query,
            (
                member_id,
                data.get("trainer_id"),
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

# PUT - Mark message as read/archived
@members.route('/messages/<int:message_id>', methods=['PUT'])
def update_message(message_id):
    try:
        data = request.get_json()
        
        # Check if message exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM message WHERE message_id = %s", (message_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Message not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["read_status"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(message_id)
        query = f"UPDATE message SET {', '.join(update_fields)} WHERE message_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Message updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

