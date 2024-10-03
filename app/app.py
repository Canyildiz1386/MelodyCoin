import os
import hmac
import hashlib
from flask import Flask, request, abort, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo

app = Flask(__name__)

# MongoDB connection configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/melodyCoinDB"
# Folder to store uploaded songs
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# Set maximum upload size (16 MB)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

mongo = PyMongo(app)

# Secret key for HMAC hashing
SECRET_KEY = "your_secret_key"
# Allowed file extensions for song uploads
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

# Ensure the base upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Generate a hash for the user using user_id and username
def generate_hash(user_id, username):
    data = f"user_id={user_id}&username={username}"
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

# Validate the hash to ensure it's authentic
def validate_hash(user_id, username, received_hash):
    expected_hash = generate_hash(user_id, username)
    return hmac.compare_digest(expected_hash, received_hash)

# Route for the input page, where users can enter or update their nickname
@app.route('/input_page', methods=['GET', 'POST'])
def input_page():
    user_id = request.args.get('user_id')
    username = request.args.get('username')
    received_hash = request.args.get('hash')

    # Validate the hash to ensure the request is authentic
    if not validate_hash(user_id, username, received_hash):
        abort(403)

    # Handle form submission (nickname)
    if request.method == 'POST':
        nickname = request.form['nickname']

        # Check if the username is unique in the database
        existing_username = mongo.db.users.find_one({"nickname": nickname})
        if existing_username:
            return "Username already exists. Please choose another one.", 400

        # Check if the user already exists based on user_id
        existing_user = mongo.db.users.find_one({"user_id": user_id})

        if not existing_user:
            # If user doesn't exist, create a new user entry
            user = {
                "user_id": user_id,
                "username": username,
                "nickname": nickname,
                "hash": received_hash,
                "level": 1,
                "profit": 0,
                "coins": 100,  # Default initial coins value
                "songs": []  # Initialize with an empty list of songs
            }
            mongo.db.users.insert_one(user)
        else:
            # If user exists, update the nickname
            mongo.db.users.update_one({"user_id": user_id}, {"$set": {"nickname": nickname}})

        # Redirect to the home page after nickname update
        return redirect(url_for('home_page', user_id=user_id, username=username, hash=received_hash, nickname=nickname))

    # Render the input page template for the user to enter nickname
    return render_template('input page/input.html', user_id=user_id, username=username, hash=received_hash)

# Route for the home page where users can see their profile and songs
@app.route('/')
def home_page():
    user_id = request.args.get('user_id')
    username = request.args.get('username')
    received_hash = request.args.get('hash')
    nickname = request.args.get('nickname')

    # Validate user parameters
    if not user_id or not username or not received_hash:
        abort(403)

    # Validate the hash
    if not validate_hash(user_id, username, received_hash):
        abort(403)

    # If nickname is missing, redirect to the input page
    if not nickname:
        return redirect(url_for('input_page', user_id=user_id, username=username, hash=received_hash))

    # Fetch user data from the database
    user = mongo.db.users.find_one({"user_id": user_id})

    if not user:
        # If the user doesn't exist, redirect to the input page
        return redirect(url_for('input_page', user_id=user_id, username=username, hash=received_hash))

    # Render the home page template with user data (including songs list)
    return render_template('home page/home.html', username=user["username"], user_id=user["user_id"], nickname=user["nickname"], level=user["level"], profit=user["profit"], coins=user["coins"], songs=user["songs"])

# Route to handle adding a song to a user's song list
@app.route('/add_song', methods=['POST'])
def add_song():
    user_id = request.form['user_id']
    song_path = request.form['song_path']

    # Fetch the user from the database
    user = mongo.db.users.find_one({"user_id": user_id})

    if not user:
        return "User not found", 404

    # Check if the user has already uploaded 10 songs
    if len(user["songs"]) >= 10:
        return "Cannot add more than 10 songs", 400

    # Add the new song path to the user's songs list
    mongo.db.users.update_one({"user_id": user_id}, {"$push": {"songs": song_path}})

    # Redirect back to the home page after song is added
    return redirect(url_for('home_page', user_id=user_id, username=user["username"], hash=user["hash"], nickname=user["nickname"]))

# Route to handle file uploads for songs
@app.route('/upload', methods=['POST'])
def upload_songs():
    user_id = request.form['user_id']

    # Check if 'songs' is in the request files
    if 'songs' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('songs')
    user = mongo.db.users.find_one({"user_id": user_id})

    # Ensure the user exists and hasn't already uploaded more than 10 songs
    if not user or len(user['songs']) >= 10:
        return "Maximum 10 songs allowed", 400

    # Create a user-specific folder
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    # Process each uploaded file
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(user_folder, filename)
            file.save(file_path)
            # Save the relative file path in the user's song list
            relative_path = os.path.join('uploads', user_id, filename)
            mongo.db.users.update_one(
                {"user_id": user_id},
                {"$push": {"songs": relative_path}}
            )

    # Redirect to the home page after successful upload
    return redirect(url_for('home_page', user_id=user_id, username=user["username"], hash=user["hash"], nickname=user["nickname"]))

if __name__ == "__main__":
    # Run the app on host 0.0.0.0, port 8000
    app.run(debug=True, host="0.0.0.0", port=8000)
