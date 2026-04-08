#backend code for credit card fraud detection project
from flask import Flask, request, jsonify
from model import train_model, predict  
import joblib

app = Flask(__name__)   
@app.route("/train", methods=["POST"])
def train():
    try:
        train_model()
        return jsonify({
            "status": "success",
            "message": "Model trained successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        result = predict(data)
        return jsonify({
            "status": "success",
            "result": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
if __name__ == "__main__":
    app.run(debug=True) 
        
    