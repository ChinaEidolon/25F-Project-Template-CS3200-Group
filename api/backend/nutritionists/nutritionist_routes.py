from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

# Create Blueprint for Nutritionist routes
nutritionists = Blueprint('nutritionists', __name__)

# GET all nutritionists 
@nutritionists.route('/nutritionists', methods=['GET'])
def get_all_nutritionists():
    try:
        current_app.logger.info('Starting get_all_nutritionists request')
        cursor = db.get_db().cursor()
        
        # Prepare the Base query
        query = "SELECT * FROM NUTRITIONIST"
        
        current_app.logger.debug(f'Executing query: {query}')
        cursor.execute(query)
        nutritionists_list = cursor.fetchall()
        cursor.close()
        
        current_app.logger.info(f'Successfully retrieved {len(nutritionists_list)} NUTRITIONISTS')
        return jsonify(nutritionists_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_nutritionists: {str(e)}')
        return jsonify({"error": str(e)}), 500

# GET specific nutritionist profile
@nutritionists.route('/nutritionists/<int:nutritionist_id>', methods=['GET'])
def get_nutritionist(nutritionist_id):
    try:
        cursor = db.get_db().cursor()
        
        # Get nutritionist details
        query = "SELECT * FROM NUTRITIONIST WHERE nutritionist_id = %s"
        cursor.execute(query, (nutritionist_id,))
        nutritionist = cursor.fetchone()
        
        if not nutritionist:
            return jsonify({"error": "Nutritionist not found"}), 404
        
        cursor.close()
        return jsonify(nutritionist), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new nutritionist profile
# Required fields: first_name, last_name
@nutritionists.route('/nutritionists', methods=['POST'])
def create_nutritionist():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["first_name", "last_name"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new nutritionist
        query = """
        INSERT INTO NUTRITIONIST (first_name, last_name)
        VALUES (%s, %s)
        """
        cursor.execute(
            query,
            (
                data["first_name"],
                data["last_name"],
            ),
        )
        
        db.get_db().commit()
        new_nutritionist_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Nutritionist created successfully", "nutritionist_id": new_nutritionist_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update nutritionist profile
@nutritionists.route('/nutritionists/<int:nutritionist_id>', methods=['PUT'])
def update_nutritionist(nutritionist_id):
    try:
        data = request.get_json()
        
        # Check if nutritionist exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM NUTRITIONIST WHERE nutritionist_id = %s", (nutritionist_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Nutritionist not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["first_name", "last_name"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(nutritionist_id)
        query = f"UPDATE NUTRITIONIST SET {', '.join(update_fields)} WHERE nutritionist_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Nutritionist updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# MEAL PLANS commands
# GET meal plans by nutritionist or member
@nutritionists.route('/meal-plans', methods=['GET'])
def get_meal_plans():
    try:
        cursor = db.get_db().cursor()
        
        # Filter (members)
        member_id = request.args.get('member_id')
        
        query = "SELECT * FROM MEAL_PLAN WHERE 1=1"
        params = []
        
        if member_id:
            query += " AND member_id = %s"
            params.append(member_id)
        
        query += " ORDER BY plan_date DESC"
        
        cursor.execute(query, params)
        plans = cursor.fetchall()
        cursor.close()
        
        return jsonify(plans), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# GET specific meal plan details
@nutritionists.route('/meal-plans/<int:plan_id>', methods=['GET'])
def get_meal_plan(plan_id):
    try:
        cursor = db.get_db().cursor()
        query = "SELECT * FROM MEAL_PLAN WHERE plan_id = %s"
        cursor.execute(query, (plan_id,))
        plan = cursor.fetchone()
        cursor.close()
        
        if not plan:
            return jsonify({"error": "Meal plan not found"}), 404
        
        return jsonify(plan), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new meal plan
# Required fields: member_id, calorie_goals, plan_date
@nutritionists.route('/meal-plans', methods=['POST'])
def create_meal_plan():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["member_id", "calorie_goals", "plan_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new meal plan
        query = """
        INSERT INTO MEAL_PLAN (member_id, calorie_goals, macro_goals, plan_date)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                data["member_id"],
                data["calorie_goals"],
                data.get("macro_goals"),
                data["plan_date"],
            ),
        )
        
        db.get_db().commit()
        new_plan_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Meal plan created successfully", "plan_id": new_plan_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update meal plan
@nutritionists.route('/meal-plans/<int:plan_id>', methods=['PUT'])
def update_meal_plan(plan_id):
    try:
        data = request.get_json()
        
        # Check if meal plan exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM MEAL_PLAN WHERE plan_id = %s", (plan_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Meal plan not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["calorie_goals", "macro_goals", "plan_date"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(plan_id)
        query = f"UPDATE MEAL_PLAN SET {', '.join(update_fields)} WHERE plan_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Meal plan updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Delete meal plan
@nutritionists.route('/meal-plans/<int:plan_id>', methods=['DELETE'])
def delete_meal_plan(plan_id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("DELETE FROM MEAL_PLAN WHERE plan_id = %s", (plan_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Meal plan deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


# FOOD LOGS commands
# GET food log entries for a member
@nutritionists.route('/food-logs', methods=['GET'])
def get_food_logs():
    try:
        cursor = db.get_db().cursor()
        
        # Filter (members)
        member_id = request.args.get('member_id')
        
        query = "SELECT * FROM FOOD_LOG WHERE 1=1"
        params = []
        
        if member_id:
            query += " AND member_id = %s"
            params.append(member_id)
        
        query += " ORDER BY log_timestamp DESC"
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        cursor.close()
        
        return jsonify(logs), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# POST - Create new food log entry
# Required fields: member_id, food, log_timestamp
@nutritionists.route('/food-logs', methods=['POST'])
def create_food_log():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["member_id", "food", "log_timestamp"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        cursor = db.get_db().cursor()
        
        # Insert new food log
        query = """
        INSERT INTO FOOD_LOG (member_id, food, log_timestamp, portion_size, calories, proteins, carbs, fats)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                data["member_id"],
                data["food"],
                data["log_timestamp"],
                data.get("portion_size"),
                data.get("calories"),
                data.get("proteins"),
                data.get("carbs"),
                data.get("fats"),
            ),
        )
        
        db.get_db().commit()
        new_log_id = cursor.lastrowid
        cursor.close()
        
        return (
            jsonify({"message": "Food log created successfully", "log_id": new_log_id}),
            201,
        )
    except Error as e:
        return jsonify({"error": str(e)}), 500

# PUT - Update food log entry
@nutritionists.route('/food-logs/<int:log_id>', methods=['PUT'])
def update_food_log(log_id):
    try:
        data = request.get_json()
        
        # Check if food log exists
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM FOOD_LOG WHERE log_id = %s", (log_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Food log not found"}), 404
        
        # Build update query 
        update_fields = []
        params = []
        allowed_fields = ["food", "portion_size", "calories", "proteins", "carbs", "fats"]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(log_id)
        query = f"UPDATE FOOD_LOG SET {', '.join(update_fields)} WHERE log_id = %s"
        
        cursor.execute(query, params)
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Food log updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# DELETE - Delete food log entry
@nutritionists.route('/food-logs/<int:log_id>', methods=['DELETE'])
def delete_food_log(log_id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("DELETE FROM FOOD_LOG WHERE log_id = %s", (log_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Food log deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500