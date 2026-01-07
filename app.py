from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
from cnnClassifier.utils.common import decodeImage
from cnnClassifier.pipeline.prediction import PredictionPipeline

# Set environment variables for encoding
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

app = Flask(__name__)
CORS(app)

class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"
        self.classifier = PredictionPipeline(self.filename)

# Initialize the ClientApp globally so routes can always find it
clApp = ClientApp()

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route("/train", methods=['GET','POST'])
@cross_origin()
def trainRoute():
    try:
        # Using main.py to trigger training
        os.system("python main.py")
        return "Training done successfully!"
    except Exception as e:
        return f"Error during training: {str(e)}"

@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
    try:
        # 1. Capture JSON data
        data = request.get_json()
        if data is None or 'image' not in data:
            return jsonify({"error": "No image data found in request"}), 400
        
        image = data['image']
        
        # 2. Decode the base64 string and save as 'inputImage.jpg'
        decodeImage(image, clApp.filename)
        
        # 3. Run prediction via the pipeline
        result = clApp.classifier.predict()
        
        # 4. Return the result as JSON
        return jsonify(result)
        
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Running on 8080 for AWS/Local testing
    app.run(host='0.0.0.0', port=8080)