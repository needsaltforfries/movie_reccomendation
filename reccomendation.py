import torch

from torch.nn.functional import cosine_similarity 
from torch.utils.data import Dataset, DataLoader
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
import string
import difflib
import os
import pandas as pd

import movieLoader
from movieLoader import MoviesDataset
import network
from network import Reccomender

# Load model and pre-process data
print("pre-processing...")
model_path = "./reccomender_model.pth"
model = Reccomender(1)  # Ensure the architecture matches the saved model
state_dict = torch.load(model_path, map_location=torch.device('cpu'))  # Load the state dictionary
model.load_state_dict(state_dict)  # Load the weights into the model
model.eval()  # Set the model to evaluation mode

#pre-process data to get most similar result
movies = pd.read_csv('tmdb_5000_movies.csv')
movies = movies.iloc[:-3]
features = ['title', 'genres', 'keywords', 'original_language', 'vote_average']

# make dataset
dataset = MoviesDataset(movies)

data = []
for i in range(len(dataset)):
    data.append(dataset[i])
data_tensor = torch.stack(data)

def getSimilarMovieIDS(IDs, num_results=1):
    print("getting similar movies")
    #pull movies from movie database
    features = []
    for i in IDs:
        features.append(dataset[movies.loc[movies['id'] == i].index[0]])
    print(features)
    #convert movie features into tensor
    for feat in features:
        with torch.no_grad():
            feat = feat.reshape(1, 5)
            tensor = model(feat)

    #get most similar movie to output tensor
    similarities = cosine_similarity(tensor, data_tensor)
    i_most_similar = torch.argmax(similarities).item()
    print(i_most_similar)
    similar_movies = torch.flip(similarities, dims=[0])
    print(similar_movies)
    for i in range(min(num_results, len(similar_movies))):
        movie_title = movies.iloc[i_most_similar]["title"]
        print(movie_title)
    return similar_movies[:num_results]

#test function
getSimilarMovieIDS([1726], 3)