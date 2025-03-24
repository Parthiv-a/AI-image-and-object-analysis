import os
import io
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Use a default secret key for development
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_development')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MongoDB Atlas setup
mongo_uri = f"mongodb+srv://abhinavkolamulliyil13:Rajavintemakan123@cluster0.5rvwa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client['image_analyzer']
users_collection = db['users']

# Azure Computer Vision setup
subscription_key = os.getenv('AZURE_COMPUTER_VISION_KEY')
endpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
vision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# User model
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']

    @staticmethod
    def get(user_id):
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            return None
        return User(user_data)

    @staticmethod
    def find_by_username(username):
        user_data = users_collection.find_one({'username': username})
        if not user_data:
            return None
        return User(user_data)

    @staticmethod
    def create(username, password):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_id = users_collection.insert_one({
            'username': username,
            'password_hash': password_hash,
            'images': []  # Initialize an empty list for storing images
        }).inserted_id
        return User.get(str(user_id))

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.find_by_username(username):
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        user = User.create(username, password)
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('profile'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.find_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    # Fetch the user's uploaded images from MongoDB
    user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
    images = user_data.get('images', [])
    return render_template('profile.html', user=current_user, images=images)

# Upload image route
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('profile'))
    
    if file:
        # Convert the image to base64 for storage in MongoDB
        image_data = file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Store the image in the user's document in MongoDB
        users_collection.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$push': {'images': image_base64}}
        )
        flash('Image uploaded successfully!', 'success')
    
    return redirect(url_for('profile'))

# Analyze image route
@app.route('/analyze/<int:image_index>')
@login_required
def analyze(image_index):
    # Fetch the user's document from MongoDB
    user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
    images = user_data.get('images', [])
    
    # Get the selected image
    try:
        image_base64 = images[image_index]
    except IndexError:
        flash('Invalid image selected', 'error')
        return redirect(url_for('profile'))
    
    # Decode the base64 image
    image_data = base64.b64decode(image_base64)
    
    # Analyze the image using Azure Computer Vision API
    analysis = analyze_image(image_data)
    
    # Render the result template with the image and analysis results
    return render_template('result.html', analysis=analysis, image_base64=image_base64)

# Compare images route
@app.route('/compare', methods=['POST'])
@login_required
def compare():
    if 'file1' not in request.files or 'file2' not in request.files:
        flash('Please upload two images', 'error')
        return redirect(url_for('profile'))
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if file1.filename == '' or file2.filename == '':
        flash('Please select two images', 'error')
        return redirect(url_for('profile'))
    
    if file1 and file2:
        # Convert the images to base64 for comparison
        image1_data = file1.read()
        image2_data = file2.read()
        
        # Compare the images using Azure Computer Vision API
        comparison_result = compare_images(image1_data, image2_data)
        
        # Render the result template with the comparison result
        return render_template('result.html', comparison_result=comparison_result)

# Function to analyze image using Azure Computer Vision API
def analyze_image(image_data):
    features = [
        VisualFeatureTypes.description,
        VisualFeatureTypes.tags,
        VisualFeatureTypes.categories,
        VisualFeatureTypes.objects
    ]
    
    # Wrap the bytes data in a file-like object
    image_stream = io.BytesIO(image_data)
    
    # Analyze the image using Azure Computer Vision API
    results = vision_client.analyze_image_in_stream(image_stream, visual_features=features)
    
    analysis = {
        "description": results.description.captions[0].text if results.description.captions else "",
        "tags": [{"name": tag.name, "confidence": f"{tag.confidence:.2f}"} for tag in results.tags],
        "categories": [{"name": category.name, "confidence": f"{category.score:.2f}"} for category in results.categories],
        "objects": [{"name": obj.object_property, "confidence": f"{obj.confidence:.2f}"} for obj in results.objects]
    }
    
    return analysis

# Function to compare images using Azure Computer Vision API
def compare_images(image1_data, image2_data):
    # Analyze both images
    analysis1 = analyze_image(image1_data)
    analysis2 = analyze_image(image2_data)
    
    # Extract tags and descriptions
    tags1 = set(tag['name'] for tag in analysis1['tags'])
    tags2 = set(tag['name'] for tag in analysis2['tags'])
    description1 = analysis1['description']
    description2 = analysis2['description']
    
    # Calculate similarity percentage based on tags
    common_tags = tags1.intersection(tags2)
    total_tags = tags1.union(tags2)
    similarity_percentage = (len(common_tags) / len(total_tags)) * 100 if total_tags else 0
    
    # Determine differences
    differences = []
    if description1 != description2:
        differences.append(f"The descriptions are different: '{description1}' vs '{description2}'.")
    
    unique_tags1 = tags1 - tags2
    unique_tags2 = tags2 - tags1
    
    if unique_tags1:
        differences.append(f"Image 1 has unique tags: {', '.join(unique_tags1)}.")
    if unique_tags2:
        differences.append(f"Image 2 has unique tags: {', '.join(unique_tags2)}.")
    
    # Prepare the comparison result
    if not differences:
        comparison_result = "The images are the same."
    else:
        comparison_result = "The images are different. " + " ".join(differences)
    
    # Add similarity percentage to the result
    comparison_result += f" The images are {similarity_percentage:.2f}% similar based on tags."
    
    return comparison_result

# Run the app
if __name__ == '__main__':
    app.run(debug=True)