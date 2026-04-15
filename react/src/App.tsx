import { Link } from 'react-router'
import './App.css'

function App() {
  return (
    <div className="landing">
      <div className="landing-bg" />
      <div className="landing-content">
        <h1 className="landing-title">
          Skylanders
          <span className="landing-title-accent">Collector</span>
        </h1>
        <p className="landing-subtitle">
          Gère ta collection de figurines Skylanders
        </p>
        <Link to="/search" className="landing-cta">
          Explorer la collection
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </div>
  )
}

export default App
