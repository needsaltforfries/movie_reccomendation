# app.py
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

import torch
from torch.nn.functional import cosine_similarity 
import movieLoader
from movieLoader import MoviesDataset
import pandas as pd

#load model and pre-process data
# model_path = "reccomender_model.pth"
# model = torch.load(model_path)
# model.eval()

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
        num_reccomendations = data.get('num_movies')
        id_list = data.get('id_list')
        print("Received data:", data)
        print(id_list)
        # min(len(movies_dataset), num_reccomendations)
        reccomendations = movies_dataset.GetSimilarItemsById(id_list, 3)
        print("Reccomended IDs: ", reccomendations)

        if len(reccomendations) == 0:
            return jsonify({"error": "No reccomendations found"}), 404
        
        return jsonify({
            "num_reccomendations": 3,
            "ids": reccomendations
        })
    except Exception as e:
            print("Error:", e)
            return jsonify({"error": "Server error"}), 500

#this route uses a neural net to get reccomendations
@app.route('/reccomend_model', methods=['POST'])
def reccomend_model():
    #do processing with ids
    #get tensor from neural net
    #get cosine similarity to tensor
    #return num_reccomendations
    pass

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)