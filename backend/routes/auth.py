from flask import Blueprint, request
from models import db, User
from flask_jwt_extended import create_access_token
from extensions import bcrypt

auth_bp = Blueprint("auth", __name__)

# ------------------------
# REGISTER
# ------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return {"error": "Missing required fields"}, 400

    if User.query.filter(
        (User.username == username) | (User.email == email)
    ).first():
        return {"error": "User already exists"}, 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "next_step": "create_profile"
    }, 201


# ------------------------
# LOGIN (JWT)
# ------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return {"error": "Email and password required"}, 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return {"error": "Invalid credentials"}, 401

    # Ensure the JWT 'sub' (subject) is a string to avoid PyJWT validation errors
    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "Login successful",
        "access_token": access_token
    }, 200
