from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import joblib
import numpy as np
from datetime import timedelta
import os
from dotenv import load_dotenv  #  Corrected import

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Corrected model file path
model_path = os.getenv("DECISION_TREE_MODEL_PATH", "best_decision_tree_model.joblib")

# Load the model with error handling
try:
    model = joblib.load(model_path)
    print(f"Model loaded successfully from: {model_path}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Secret key for JWT and token expiration
# Load secret key from .env
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback_secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)  # Token lasts 6 hours

# Initialize JWT
jwt = JWTManager(app)

# Dummy user data (replace with a database in real projects)
users = {"admin": "password123"}

# Route to serve the HTML form
@app.route("/")
def home():
    return render_template("index.html")  # This serves the form.html file

# Route to login and get a token
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

    return jsonify({"message": "Invalid credentials"}), 401

# Protected route for making predictions
@app.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    try:
        data = request.json  # Get the JSON payload
        features = np.array(list(data.values())).reshape(1, -1)  # Convert to NumPy array

        # Make prediction
        prediction = model.predict(features)[0]

        return jsonify({"prediction": int(prediction)})  # Convert NumPy int to regular int
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Run the app
#if __name__ == "__main__":
    #app.run(debug=True)

if __name__ == "__main__":
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)