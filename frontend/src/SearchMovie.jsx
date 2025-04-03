import { useState } from "react";
import { useNavigate } from "react-router-dom";

function SearchMovie(){
    const BASEURL = `https://api.themoviedb.org/3`;
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [selectedMovies, setSelectedMovies] = useState([]); // Store only movie IDs
    const [recCount, setRecCount] = useState(3);
    const navigate = useNavigate();

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

    const CSRecommendation = async () => {
        const payload = {
            rec_count: recCount,
            id_list: selectedMovies.map((movie)=>movie.id), // Send only the IDs to the backend
        };
        try {
            if (payload.id_list.length === 0) {
                alert('Please select at least one movie');
                return;
            }
            const response = await fetch('http://localhost:5000/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
            });

            const result = await response.json();
            if(response.ok) {
                console.log(result); // Log the response from the backend
                navigate('/results', { state: { result, recCount } }); // Navigate to the results page with the response data
            }
            else{
                if (result.error === "No recommendations found") {
                    alert('No recommendations found. Please try again with different movies.');
                }
                alert(`Error: ${result.error}`);
                console.log(`Error: ${result.error}`); // Log the error message from the backend
            }
        } catch (error) {
            console.error('Error sending data:', error);
        }
    };
    const AIReccomendation = async () => {
        const payload = {
            rec_count: recCount,
            movies: selectedMovies, // Send only the IDs to the backend
        };
        try {
            if (payload.movies.length === 0) {
                alert('Please select at least one movie');
                return;
            }
            const response = await fetch('http://localhost:5000/recommend_AI', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
            });

            const result = await response.json();
            if(response.ok) {
                console.log(result); // Log the response from the backend
                navigate('/results', { state: { result, recCount } }); // Navigate to the results page with the response data
            }
            else{
                console.log(result)
                if (result.error === "No recommendations found") {
                    alert('No recommendations found. Please try again with different movies.');
                }
                alert(`Error: ${result.error}`);
                console.log(`Error: ${result.error}`); // Log the error message from the backend
            }
        } catch (error) {
            console.error('Error sending data:', error);
        }
    };

    const handleMovieClick = (movie) => {
        if (movie && !selectedMovies.some((selected) => selected.id === movie.id)) {
            setSelectedMovies((prevSelectedMovies) => [...prevSelectedMovies, movie]); // Add the movie only if it's not already selected
            console.log(`Selected movie IDs:`, [...selectedMovies, movie.id]); // Log the updated array
        } else {
            console.log(`Movie with ID ${movie.id} is already selected.`);
        }
    };

    const handleRemoveMovie = (id) => {
        setSelectedMovies((prevSelectedMovies) =>
            prevSelectedMovies.filter((movie) => movie.id !== id) // Filter by movie.id
        );
    };

    return (
    <div className="app-container">
        <div className="main-content">
        <h2>Movie Recomendation App</h2>
        <div>
            <input
            type="text"
            placeholder="Search for a movie..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            />
            <input
                type="number"
                min="1"
                max="10" // Set the maximum number of recommendations to 10
                placeholder="Number of recommendations"
                style={{ marginLeft: '10px' }} // Add spacing between the button and input
                value={recCount}
                onChange={(e) => {
                    const value = Math.min(Number(e.target.value), 10); // Ensure the value does not exceed 10
                    setRecCount(value);
                }}
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
        
        </div>

        <div className="sidebar">
        <h2>Selected Movies</h2>
        <ul>
            {selectedMovies.map((movie) => (
            <li key={movie.id}>
                {movie.title}
                <button className="button-primary" onClick={() => handleRemoveMovie(movie.id)}>Remove</button>
            </li>
            ))}
        </ul>
        <button onClick={CSRecommendation} className="button-secondary">Recommend</button>
        <button onClick={AIReccomendation} className="button-secondary">Recommend using AI</button>

        </div>
    </div>
    );
}

export default SearchMovie;