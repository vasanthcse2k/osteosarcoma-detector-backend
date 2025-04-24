from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import imagehash
import os

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Build hash map once at startup
def build_hash_map(base_dir="dataset"):
    hash_map = {}
    for label in ['affected', 'not_affected']:
        folder = os.path.join(base_dir, label)
        if not os.path.exists(folder):
            print(f"Warning: Missing folder {folder}")
            continue
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            try:
                img = Image.open(filepath)
                img_hash = str(imagehash.average_hash(img))
                hash_map[img_hash] = label
            except Exception as e:
                print(f"Skipping {filename}: {e}")
    return hash_map

# Initialize hash map once
hash_map = build_hash_map("dataset")

# Prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    try:
        img = Image.open(file.stream)
        img_hash = str(imagehash.average_hash(img))
        label = hash_map.get(img_hash, 'Unknown')
        return jsonify({'prediction': label})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run server
if __name__ == '__main__':
    app.run(debug=True)
