# app.py
from flask import Flask, jsonify, send_from_directory, make_response
from flask import request
from flask_cors import CORS

import torch
import numpy as np
from torch.nn.functional import cosine_similarity 
import movieLoader
from movieLoader import MoviesDataset
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import network
from network import Reccomender

# Load model and pre-process data
model_path = "model.pth"
model = Reccomender(1)  # Initialize the model architecture
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))  # Load the state_dict
#initialize Flask app
app = Flask(__name__, static_folder = './client/dist', static_url_path = '/')

#enable CORS for this origin
CORS(app, origins=["http://localhost:5173"])

#load data
dp = pd.read_csv('./tmdb_5000_movies.csv')
movies_dataset = MoviesDataset(dp)

#default route test
@app.route('/')
def hello_world():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('./client/dist', filename, mimetype='application/javascript')

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
        mdf['title'] = mdf['title'].fillna('Unknown')
        mdf['overview'] = mdf['overview'].fillna('Unknown')
        mdf['title'] = mdf['title'].apply(movies_dataset.clean_text)
        mdf['overview'] = mdf['overview'].apply(movies_dataset.clean_text)

        features = mdf['title'] + ' ' + mdf['overview']
        # Convert text data to TF-IDF vectors
        vctr = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vctr.fit_transform(features)

        # Aggregate the reduced vectors
        aggregated_vector = np.mean(tfidf_matrix.toarray(), axis=0)  # Convert sparse matrix to dense and aggregate
        if len(aggregated_vector) < 32:
            # Pad with zeroes if the vector is shorter than 32
            aggregated_vector = np.pad(aggregated_vector, (0, 32 - len(aggregated_vector)), mode='constant')
        else:
            # Slice to ensure the vector has exactly 32 elements
            aggregated_vector = aggregated_vector[:32]
        aggregated_tensor = torch.tensor(aggregated_vector, dtype=torch.float32).unsqueeze(0).unsqueeze(1)

        # Pass the tensor to the neural network
        output_tensor = model(aggregated_tensor).detach().numpy()
        # Get recommendations
        recommendations = movies_dataset.GetSimilarItems(output_tensor, rec_count)
        print("Recommended IDs: ", recommendations)

        if len(recommendations) == 0:
            return jsonify({"error": "No recommendations found"}), 404

        return jsonify({
            "ids": recommendations
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)