import { useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './Results.css'; // Add a CSS file for styling the grid

async function getItem(id) {
    console.log("Fetching movie with ID:", id); // Log the ID being fetched
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
    if (!response.ok) {
        console.error(`Error fetching movie with ID ${id}:`, response.status, response.statusText);
        return null;
    }
    const data = await response.json();
    console.log("Fetched data for ID:", id, data); // Log the fetched data
    return data;
}

function Results() {

    const location = useLocation(); // Access the state passed from App.jsx
    const { result } = location.state || {}; // Destructure the result from state
    const [movies, setMovies] = useState([]); // Initialize movies state
    useEffect(() => {
        const fetchMovies = async () => {
            console.log("All ids to get:", result.ids);

            // Flatten result.ids if it contains nested arrays
            const ids = Array.isArray(result.ids[0]) ? result.ids[0] : result.ids;

            if (result && Array.isArray(ids)) {
                try {
                    // Use Promise.all to fetch all movies concurrently
                    const movieData = await Promise.all(
                        ids.map(async (id) => {
                            console.log(`Fetching movie with ID: ${id}`);
                            const movie = await getItem(id); // Fetch each movie data
                            console.log(`Got movie for ID: ${id}`, movie);
                            return movie; // Return the movie data
                        })
                    );

                    console.log("All fetched movies:", movieData);
                    // Filter out null responses and set the movies
                    setMovies(movieData.filter(movie => movie !== null));
                } catch (error) {
                    console.error("Error fetching movies:", error);
                }
            } else {
                console.warn("result.ids is not an array or is undefined:", result.ids);
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
                                src={
                                    movie.poster_path
                                        ? `https://image.tmdb.org/t/p/w200${movie.poster_path}`
                                        : "https://via.placeholder.com/200x300?text=No+Image"
                                }
                                alt={movie.title || "No Title"}
                            />
                            <h3>{movie.title || "No Title Available"}</h3>
                            <p>{movie.overview || "No description available."}</p>
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