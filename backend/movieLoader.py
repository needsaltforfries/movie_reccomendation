import torch
from torch.utils.data import Dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

import string
import numpy as np

class MoviesDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform
        self.vctr = TfidfVectorizer(stop_words='english')
        features = ['title', 'genres', 'keywords', 'original_language', 'vote_average']
        
        # Fill missing values with 'Unknown' for string columns
        for feature in features:
            self.data[feature] = self.data[feature].fillna('Unknown')
        
        # Clean the text columns
        self.data['keywords'] = self.data['keywords'].apply(self.clean_text)
        self.data['title'] = self.data['title'].apply(self.clean_text)
        self.data['genres'] = self.data['genres'].apply(self.clean_text)
        self.data['original_language'] = self.data['original_language'].apply(self.clean_text)

        scaler = StandardScaler()

        weight_title = 2.0  # Increase the weight of title
        weight_genre = 1.5  # Increase the weight of genre
        
        vectorizer_title = TfidfVectorizer()
        vectorizer_genre = TfidfVectorizer()
        vectorizer_keywords = TfidfVectorizer()
        vectorizer_language = TfidfVectorizer()
        
        title_features = self.data['title']
        genre_features = self.data['genres']
        keywords_features = self.data['keywords']
        language_features = self.data['original_language']
        vote_avg = self.data['vote_average'].values.reshape(-1, 1)
        
        title_vec = vectorizer_title.fit_transform(title_features)
        genre_vec = vectorizer_genre.fit_transform(genre_features)
        keywords_vec = vectorizer_keywords.fit_transform(keywords_features)
        language_vec = vectorizer_language.fit_transform(language_features)

        title_vec_scaled = scaler.fit_transform(title_vec.toarray())
        genre_vec_scaled = scaler.fit_transform(genre_vec.toarray())
        keywords_vec_scaled = scaler.fit_transform(keywords_vec.toarray())
        language_vec_scaled = scaler.fit_transform(language_vec.toarray())

        feat_vectors = np.concatenate([
            weight_title * title_vec_scaled,
            weight_genre * genre_vec_scaled,
            keywords_vec_scaled,
            language_vec_scaled
        ], axis=1)
        feat_vectors = np.concatenate([feat_vectors, vote_avg], axis=1)

        svd = TruncatedSVD(n_components=32) 
        self.feat_vectors = np.concatenate([feat_vectors, vote_avg], axis=1)
        
        svd = TruncatedSVD(n_components=32)  # Reduce to 2 dimensions for visualization
        self.reduced_features = svd.fit_transform(feat_vectors).astype(np.float32)
        self.similarity = cosine_similarity(self.reduced_features)
        
    def clean_text(self, text):
        """Clean text by removing punctuation and stripping extra spaces."""
        text = text.strip().lower()
        text = ''.join([char for char in text if char not in string.punctuation])
        if not text or text.isspace():
            return 'Unknown'
        return text
    
    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data.iloc[idx]
        return torch.tensor(self.reduced_features[idx])
    
    def GetSimilarItems(self, vec, top_n=5):
        vec = vec.reshape(1, -1)
        sim = torch.tensor(cosine_similarity(vec, self.reduced_features))
        # closest_index = torch.argmax(sim).item()
        
        most_similar_idxs = np.argsort(sim[0].numpy())[::-1][:top_n]
        
        return self.data.iloc[most_similar_idxs]['id'].tolist()
    
    def GetSimilarItemsById(self, id_list, top_n=1):
        results = []
        for i in range(len(id_list)):
            item = self.data.loc[self.data['id'] == id_list[i]]

            # Check if the item exists
            if item.empty:
                print(f"ID {id_list[i]} not found in the dataset.")
                continue
            
            idx = item.index[0]
            most_similar_idxs = np.argsort(self.similarity[idx])[::-1][1:min(len(self.data), top_n+1)]
            results.append(self.data.iloc[most_similar_idxs]['id'].tolist())
        print(results)
        return results