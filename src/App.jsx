import { useState } from 'react';
import './App.css';

const BASEURL = `https://api.themoviedb.org/3`;

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedMovies, setSelectedMovies] = useState([]); // Store only movie IDs

  const fetchMovies = async () => {
    const API_KEY = import.meta.env.VITE_READ_ACCESS_TOKEN;
    const url = `${BASEURL}/search/movie?query=${encodeURIComponent(searchQuery)}`;
    try {
      console.log(url);
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${API_KEY}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSearchResults(data.results);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const sendDataToBackend = async () => {
    const payload = {
      num_movies: selectedMovies.length,
      id_list: selectedMovies, // Send only the IDs to the backend
    };
    try {
      if (payload.id_list.length === 0) {
        alert('Please select at least one movie');
        return;
      }
      const response = await fetch('http://localhost:5000/reccomend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      console.log(result); // Log the response from the backend
    } catch (error) {
      console.error('Error sending data:', error);
    }
  };

  const handleMovieClick = (movie) => {
    if (movie && !selectedMovies.includes(movie.id)) {
      setSelectedMovies((prevSelectedMovies) => [...prevSelectedMovies, movie.id]); // Use functional update
    }
    console.log(`Selected movie IDs:`, [...selectedMovies, movie.id]); // Log the updated array
  };

  const handleRemoveMovie = (id) => {
    setSelectedMovies((prevSelectedMovies) =>
      prevSelectedMovies.filter((movieId) => movieId !== id)
    );
  };

  return (
    <div className="app-container">
      <div className="main-content">
        <div>
          <input
            type="text"
            placeholder="Search for a movie..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button onClick={fetchMovies}>Search</button>
        </div>

        <div>
          <h2>Search Results:</h2>
          <div className="movie-grid">
            {searchResults.map((movie) => (
              <div
                key={movie.id}
                className="movie-card"
                onClick={() => handleMovieClick(movie)}
              >
                <img
                  src={`https://image.tmdb.org/t/p/w200${movie.poster_path}`}
                  alt={movie.title}
                />
                <h3>{movie.title}</h3>
                <p>{movie.overview}</p>
              </div>
            ))}
          </div>
        </div>
        <button onClick={sendDataToBackend}>Send Data</button>
      </div>

      <div className="sidebar">
        <h2>Selected Movies</h2>
        <ul>
          {selectedMovies.map((id) => (
            <li key={id}>
              Movie ID: {id}{' '}
              <button onClick={() => handleRemoveMovie(id)}>Remove</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
