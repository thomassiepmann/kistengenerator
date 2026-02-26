import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ArtikelVerwaltung from './pages/ArtikelVerwaltung';
import Preispflege from './pages/Preispflege';
import Wochenplanung from './pages/Wochenplanung';
import Generator from './pages/Generator';
import Masterplaene from './pages/Masterplaene';
import Historie from './pages/Historie';
import Einstellungen from './pages/Einstellungen';
import './styles/global.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/generator" element={<Generator />} />
        <Route path="/artikel" element={<ArtikelVerwaltung />} />
        <Route path="/preise" element={<Preispflege />} />
        <Route path="/wochenquelle" element={<Wochenplanung />} />
        <Route path="/masterplaene" element={<Masterplaene />} />
        <Route path="/historie" element={<Historie />} />
        <Route path="/einstellungen" element={<Einstellungen />} />
      </Routes>
    </Router>
  );
}

export default App;
