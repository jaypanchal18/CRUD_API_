from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
import bcrypt
import uuid
import random
import string
import datetime

app = Flask(__name__)

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/user'
mongo = PyMongo(app)

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'e6580f87eb7fe5378219c529bfac2ff004b3f60864a2cc3c0bac8a7a40698092'
jwt = JWTManager(app)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jay.nit47@gmail.com'
app.config['MAIL_PASSWORD'] = 'xjzi akki ibaz dmam'
app.config['MAIL_DEFAULT_SENDER'] = 'Crud Operation''jay.nit47@gmail.com'
mail = Mail(app)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    mobile = data.get('mobile')

    users = mongo.db.users
    existing_user = users.find_one({'$or': [{'email': email}, {'mobile': mobile}]})

    if existing_user:
        return jsonify({"msg": "User with this email or mobile number already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    verification_token = str(uuid.uuid4())

    user_data = {
        'username': username,
        'password': hashed_password,
        'email': email,
        'mobile': mobile,
        'verified': False,
        'verification_token': verification_token
    }
    users.insert_one(user_data)

    # Debug statement
    print("User added to MongoDB, sending email...")

    # Send verification email
    verification_link = f'http://localhost:3000/verify/{verification_token}'
    msg = Message('Verify Your Email', recipients=[email])
    msg.body = f"""Hello {username},

Thank you for registering with our service. 

Please verify your email address by clicking the following link:
{verification_link}

For your reference, here are your registration details:
- **Username:** {username}
- **Password:** {password}

Please keep this information safe. If you did not register for this account, please ignore this email.

Best regards,
"""
    mail.send(msg)

    return jsonify({"msg": "User created successfully. Please check your email for verification."}), 201

@app.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    users = mongo.db.users
    user = users.find_one({'verification_token': token})

    if not user:
        return jsonify({"msg": "Invalid or expired verification token"}), 400

    users.update_one({'verification_token': token}, {'$set': {'verified': True, 'verification_token': None}})

    return jsonify({"msg": "Email verified successfully. You can now log in."}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    users = mongo.db.users
    user = users.find_one({'username': username})

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"msg": "Invalid username or password"}), 401

    if not user['verified']:
        return jsonify({"msg": "Please verify your email address. Check your inbox for the verification link."}), 403

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    users = mongo.db.users
    user = users.find_one({'email': email})

    if not user:
        return jsonify({"msg": "No user found with this email address"}), 404

    # Generate a 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=10)  # OTP valid for 10 minutes

    users.update_one({'email': email}, {'$set': {'otp': otp, 'otp_expiry': otp_expiry}})

    msg = Message('Your OTP Code', recipients=[email])
    msg.body = f"""Hello,

Here is your OTP code for password reset:

{otp}

This OTP is valid for 10 minutes. If you did not request this, please ignore this email.

Best regards,
"""
    mail.send(msg)

    return jsonify({"msg": "OTP has been sent to your email."}), 200



@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('password')

    users = mongo.db.users
    user = users.find_one({'email': email})

    if not user:
        return jsonify({"msg": "No user found with this email address"}), 404

    # Check OTP validity
    if user.get('otp') != otp or datetime.datetime.now() > user.get('otp_expiry'):
        return jsonify({"msg": "Invalid or expired OTP"}), 400

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    users.update_one({'email': email}, {'$set': {'password': hashed_password, 'otp': None, 'otp_expiry': None}})

    return jsonify({"msg": "Password has been reset successfully. You can now log in with your new password."}), 200


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200



@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    users = mongo.db.users
    user = users.find_one({'username': current_user}, {'_id': 0, 'password': 0, 'verification_token': 0})
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"msg": "User not found"}), 404

@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    data = request.get_json()
    users = mongo.db.users

    update_data = {
        'username': data.get('username'),
        'email': data.get('email'),
        'mobile': data.get('mobile')
    }

    result = users.update_one({'username': current_user}, {'$set': update_data})

    if result.modified_count == 1:
        return jsonify({"msg": "Profile updated successfully"}), 200
    else:
        return jsonify({"msg": "Profile update failed"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
