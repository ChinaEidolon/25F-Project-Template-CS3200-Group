from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error

# Create Blueprint
members = Blueprint('members', __name__)

# ==================== MEMBERS ====================

# GET all members (filtered by status, trainer, or nutritionist)
@members.route('/members', methods=['GET'])
def get_all_members():
    try:
        cursor = db.get_db().cursor()
        
        # Get query parameters for filtering
        status = request.args.get('status')
        trainer_id = request.args.get('trainer_id')
        nutritionist_id = request.args.get('nutritionist_id')
        
        query = "SELECT * FROM gym_member WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        if trainer_id:
            query += " AND trainer_id = %s"
            params.append(trainer_id)
        if nutritionist_id:
            query += " AND nutritionist_id = %s"
            params.append(nutritionist_id)
        
        cursor.execute(query, params)
        members = cursor.fetchall()
        cursor.close()
        
        return jsonify(members), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# GET specific member profile
@members.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        cursor = db.get_db().cursor()
        query = "SELECT * FROM gym_member WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        member = cursor.fetchone()
        cursor.close()
        
        if not member:
            return jsonify({"error": "Member not found"}), 404
        
        return jsonify(member), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new member
@members.route('/members', methods=['POST'])
def create_member():
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'first_name' not in data or 'last_name' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        cursor = db.get_db().cursor()
        query = """
            INSERT INTO gym_member (first_name, last_name, trainer_id, nutritionist_id, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['first_name'],
            data['last_name'],
            data.get('trainer_id'),
            data.get('nutritionist_id'),
            data.get('status', 'active')
        ))
        
        db.get_db().commit()
        new_member_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({"message": "Member created", "member_id": new_member_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update member profile
@members.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        allowed_fields = ['first_name', 'last_name', 'trainer_id', 'nutritionist_id', 'status']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(member_id)
        query = f"UPDATE gym_member SET {', '.join(update_fields)} WHERE member_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Member updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Deactivate member (soft delete)
@members.route('/members/<int:member_id>', methods=['DELETE'])
def deactivate_member(member_id):
    try:
        cursor = db.get_db().cursor()
        query = "UPDATE gym_member SET status = 'cancelled' WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Member deactivated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# ==================== GOALS ====================

# GET all goals for a member
@members.route('/members/<int:member_id>/goals', methods=['GET'])
def get_member_goals(member_id):
    try:
        cursor = db.get_db().cursor()
        # Note: Adjust table name if your goals table is named differently
        query = "SELECT * FROM goal WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        goals = cursor.fetchall()
        cursor.close()
        
        return jsonify(goals), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new goal
@members.route('/members/<int:member_id>/goals', methods=['POST'])
def create_goal(member_id):
    try:
        data = request.get_json()
        
        cursor = db.get_db().cursor()
        query = """
            INSERT INTO goal (member_id, goal_type, target_value, current_value, deadline)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            member_id,
            data.get('goal_type'),
            data.get('target_value'),
            data.get('current_value'),
            data.get('deadline')
        ))
        
        db.get_db().commit()
        new_goal_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({"message": "Goal created", "goal_id": new_goal_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update goal
@members.route('/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()
        
        update_fields = []
        params = []
        
        allowed_fields = ['target_value', 'current_value', 'deadline', 'goal_type']
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
        
        return jsonify({"message": "Goal updated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Delete/retire a goal
@members.route('/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    try:
        cursor = db.get_db().cursor()
        query = "DELETE FROM goal WHERE goal_id = %s"
        cursor.execute(query, (goal_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Goal deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# ==================== WORKOUT LOGS ====================

# GET workout logs for a member
@members.route('/members/<int:member_id>/workout-logs', methods=['GET'])
def get_workout_logs(member_id):
    try:
        cursor = db.get_db().cursor()
        query = """
            SELECT * FROM workout_log 
            WHERE member_id = %s 
            ORDER BY workout_date DESC
        """
        cursor.execute(query, (member_id,))
        logs = cursor.fetchall()
        cursor.close()
        
        return jsonify(logs), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Log new workout
@members.route('/members/<int:member_id>/workout-logs', methods=['POST'])
def create_workout_log(member_id):
    try:
        data = request.get_json()
        
        cursor = db.get_db().cursor()
        query = """
            INSERT INTO workout_log (member_id, trainer_id, workout_date, notes, sessions)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            member_id,
            data.get('trainer_id'),
            data['workout_date'],
            data.get('notes'),
            data.get('sessions', 1)
        ))
        
        db.get_db().commit()
        new_log_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({"message": "Workout logged", "log_id": new_log_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

# ==================== PROGRESS ====================

# GET progress for a member
@members.route('/members/<int:member_id>/progress', methods=['GET'])
def get_progress(member_id):
    try:
        cursor = db.get_db().cursor()
        query = """
            SELECT * FROM progress 
            WHERE member_id = %s 
            ORDER BY progress_date DESC
        """
        cursor.execute(query, (member_id,))
        progress = cursor.fetchall()
        cursor.close()
        
        return jsonify(progress), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new progress entry
@members.route('/members/<int:member_id>/progress', methods=['POST'])
def create_progress(member_id):
    try:
        data = request.get_json()
        
        cursor = db.get_db().cursor()
        query = """
            INSERT INTO progress (member_id, progress_date, weight, body_fat_percentage, measurements, photos)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            member_id,
            data['progress_date'],
            data.get('weight'),
            data.get('body_fat_percentage'),
            data.get('measurements'),
            data.get('photos')
        ))
        
        db.get_db().commit()
        new_progress_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({"message": "Progress recorded", "progress_id": new_progress_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update progress entry
@members.route('/progress/<int:progress_id>', methods=['PUT'])
def update_progress(progress_id):
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()
        
        update_fields = []
        params = []
        
        allowed_fields = ['weight', 'body_fat_percentage', 'measurements', 'photos']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(progress_id)
        query = f"UPDATE progress SET {', '.join(update_fields)} WHERE progress_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Progress updated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Delete mistaken progress entry
@members.route('/progress/<int:progress_id>', methods=['DELETE'])
def delete_progress(progress_id):
    try:
        cursor = db.get_db().cursor()
        query = "DELETE FROM progress WHERE progress_id = %s"
        cursor.execute(query, (progress_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Progress entry deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500