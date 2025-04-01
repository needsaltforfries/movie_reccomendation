import { useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './Results.css'; // Add a CSS file for styling the grid

async function getItem(id){
    const BASEURL = `https://api.themoviedb.org/3`;
    const API_KEY = import.meta.env.VITE_READ_ACCESS_TOKEN;
    const url = `${BASEURL}/movie/${id}`;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${API_KEY}`,
            'Content-Type': 'application/json',
        },
    });
    return response.json();
}

function Results() {

    const location = useLocation(); // Access the state passed from App.jsx
    const { result } = location.state || {}; // Destructure the result from state
    const [movies, setMovies] = useState([]); // Initialize movies state
    console.log("results: " + JSON.stringify(result, null, 2)); // Log the result for debugging
    useEffect(() => {
        const fetchMovies = async () => {
            console.log("Fetching movies for ids:", result.ids);
            if (result && result.ids) {
                try {
                    const movieData = await Promise.all(
                        result.ids.map(async (id) => {
                            const movie = await getItem(id); // Fetch each movie data
                            return movie; // Return the movie data
                        })
                    );
                    console.log(movieData); // Log the movie data for debugging
                    // Filter out null responses and set the movies
                    setMovies(movieData.filter(movie => movie !== null));
                } catch (error) {
                    console.error('Error fetching data:', error);
                }
                
            }
        };

        fetchMovies(); // Call fetchMovies when component mounts
    }, [result]); // Dependency array makes sure to re-run this when `result` changes
    return (
        <div className="results-container">
          <h1>Results</h1>
          {movies && movies.length > 0 ? (
            <div className="movie-grid">
              {movies.map((movie) => (
                <div key={movie.id} className="movie-card">
                  <img
                    src={`https://image.tmdb.org/t/p/w200${movie.poster_path}`}
                    alt={movie.title}
                  />
                  <h3>{movie.title}</h3>
                  <p>{movie.overview}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>Loading results...</p>
          )}
        </div>
    );
}

export default Results;