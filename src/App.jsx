import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // const [count, setCount] = useState(0)
  // console.log(apiKey)
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const apiKey = import.meta.env.VITE_API_KEY
  useEffect(() => {
    // Fetch the list of popular movies
    const fetchMovies = async () => {
      try {
        const response = await fetch(
          `https://api.themoviedb.org/3/movie/popular?api_key=${apiKey}&language=en-US&page=1`
        );

        if (!response.ok) {
          throw new Error('Error fetching the data');
        }

        const data = await response.json();
        setMovies(data.results); // Store the movies list in state
      } catch (err) {
        setError(err.message); // Handle error if the API call fails
      } finally {
        setLoading(false); // Set loading to false after the request completes
      }
    };

    fetchMovies();
  }, [apiKey]); // Only run once when the component mounts

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div className="App">
      <h1>Popular Movies</h1>
      <div className="movies-list">
        {movies.map((movie) => (
          <div key={movie.id} className="movie">
            <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
            <h2>{movie.title}</h2>
            <p>{movie.overview}</p>
          </div>
        ))}
      </div> 
    </div>
  )
}

export default App
