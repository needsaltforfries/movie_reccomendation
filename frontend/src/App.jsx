import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SearchMovie from './SearchMovie';
import Results from './Results';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SearchMovie />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </Router>
  );
}

export default App;
