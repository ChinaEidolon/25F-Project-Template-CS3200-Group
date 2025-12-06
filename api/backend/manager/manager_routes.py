from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

managers = Blueprint("managers", __name__)

@managers.route('/managers', methods=['GET'])
def get_all_members():



@managers.route('/managers/<int:member_id>', methods=['GET'])
def get_member(member_id):


@managers.route('/managers', methods=['POST'])



