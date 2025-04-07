import torch
from torch.utils.data import Dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import string
import numpy as np
from scipy.sparse import hstack

class MoviesDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform

        # Fill missing values with 'Unknown' for string columns
        features = ['title', 'genres', 'keywords', 'original_language', 'overview', 'vote_average']
        for feature in features:
            self.data[feature] = self.data[feature].fillna('Unknown')

        # Combine all text features into a single column
        combined_features = (
            self.data['title'] + ' ' +
            self.data['genres'] + ' ' +
            self.data['keywords'] + ' ' +
            self.data['original_language'] + ' ' +
            self.data['overview']
        )

        # Apply TF-IDF to the combined text
        vctr = TfidfVectorizer(stop_words='english', max_features=10000)  # Limit to top 5000 features
        feat_vectors = vctr.fit_transform(combined_features)

        # Apply TruncatedSVD directly to the sparse matrix
        svd = TruncatedSVD(n_components=32)
        self.reduced_features = svd.fit_transform(feat_vectors).astype(np.float32)

        # Precompute similarity matrix
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
        return torch.tensor(self.reduced_features[idx])

    def GetSimilarItems(self, vec, top_n=5):
        vec = vec.reshape(1, -1)
        sim = torch.tensor(cosine_similarity(vec, self.reduced_features))
        most_similar_idxs = np.argsort(sim[0].numpy())[::-1][:top_n]
        return self.data.iloc[most_similar_idxs]['id'].tolist()

    def GetSimilarItemsById(self, id_list, top_n=1):
        results = []
        for movie_id in id_list:
            item = self.data.loc[self.data['id'] == movie_id]
            if item.empty:
                print(f"ID {movie_id} not found in the dataset.")
                continue
            idx = item.index[0]
            most_similar_idxs = np.argsort(self.similarity[idx])[::-1][1:top_n + 1]
            results.append(self.data.iloc[most_similar_idxs]['id'].tolist())
        return results