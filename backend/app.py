# app.py
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

import torch
import numpy as np
from torch.nn.functional import cosine_similarity 
import movieLoader
from movieLoader import MoviesDataset
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

# Load model and pre-process data
model_path = "model.pth"
model = torch.load(model_path, map_location=torch.device('cpu'))  # Map the model to the CPU

#initialize Flask app
app = Flask(__name__)

#enable CORS for this origin
CORS(app, origins=["http://localhost:5173"])

#load data
dp = pd.read_csv('./tmdb_5000_movies.csv')
movies_dataset = MoviesDataset(dp)

#default route test
@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello from Flask!"})

#this route uses similarity matrix to get reccomendations
@app.route('/recommend', methods=['POST'])
def reccomend():
    try:
        data = request.get_json()
        rec_count = int(data.get('rec_count'))
        id_list = data.get('id_list')
        print("Received data:", data)
        print(id_list)
        # min(len(movies_dataset), num_reccomendations)
        reccomendations = movies_dataset.GetSimilarItemsById(id_list, rec_count)
        print("Reccomended IDs: ", reccomendations)

        if len(reccomendations) == 0:
            return jsonify({"error": "No recommendations found"}), 404
        
        return jsonify({
            "num_recommendations": 3,
            "ids": reccomendations
        })
    except Exception as e:
            print("Error:", e)
            return jsonify({"error": "Server error"}), 500

#this route uses a neural net to get reccomendations
@app.route('/recommend_AI', methods=['POST'])
def reccomend_AI():
    try:
        data = request.get_json()
        rec_count = int(data.get('rec_count'))
        movies = data.get('movies')
        mdf = pd.DataFrame(movies)

        # Ensure features are valid
        features = ['title', 'overview']
        # Convert text data to TF-IDF vectors
        vctr = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vctr.fit_transform(features)

        # Validate TF-IDF matrix
        if tfidf_matrix.shape[0] == 0 or tfidf_matrix.shape[1] == 0:
            return jsonify({"error": "Invalid input data"}), 400

        # Apply TruncatedSVD for dimensionality reduction
        svd = TruncatedSVD(n_components=32)
        reduced_movies = svd.fit_transform(tfidf_matrix)

        # Aggregate the reduced vectors
        aggregated_vector = np.mean(reduced_movies, axis=0)
        aggregated_tensor = torch.tensor(aggregated_vector, dtype=torch.float32).unsqueeze(0)

        # Pass the tensor to the neural network
        output_tensor = model(aggregated_tensor)

        # Get recommendations
        recommendations = movies_dataset.GetSimilarItems(output_tensor, rec_count)
        print("Recommended IDs: ", recommendations)

        if len(recommendations) == 0:
            return jsonify({"error": "No recommendations found"}), 404

        return jsonify({
            "num_recommendations": len(recommendations),
            "ids": recommendations
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)