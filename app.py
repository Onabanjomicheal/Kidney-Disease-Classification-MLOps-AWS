from flask import Flask, request, jsonify, render_template
import os
import shutil
from flask_cors import CORS, cross_origin
from cnnClassifier.utils.common import decodeImage
from cnnClassifier.pipeline.prediction import PredictionPipeline

# Set environment variables for encoding
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

app = Flask(__name__)
CORS(app)

# --- START ADJUSTMENT: Copy logic on startup ---
source_model = os.path.join("artifacts", "training", "model.h5")
target_dir = "model"
target_model = os.path.join(target_dir, "model.h5")

# Create the folder and copy the model immediately when app.py runs
os.makedirs(target_dir, exist_ok=True)
if os.path.exists(source_model):
    shutil.copy(source_model, target_model)
    print("--- Model successfully copied to /model folder ---")
# --- END ADJUSTMENT ---

class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"
        self.classifier = PredictionPipeline(self.filename)

# Initialize the ClientApp globally
clApp = ClientApp()

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route("/train", methods=['GET','POST'])
@cross_origin()
def trainRoute():
    try:
        # Run training
        os.system("python main.py")
        # os.system("dvc repro")
        
        # Sync again after training in case a newer model was created
        if os.path.exists(source_model):
            shutil.copy(source_model, target_model)
            
        return "Training and copy successful!"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
    try:
        data = request.get_json()
        if data is None or 'image' not in data:
            return jsonify({"error": "No image data found"}), 400
        
        image = data['image']
        decodeImage(image, clApp.filename)
        
        # This uses the model in the /model folder created above
        result = clApp.classifier.predict()
        return jsonify(result)
        
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)