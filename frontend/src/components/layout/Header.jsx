import { Bell, User } from 'lucide-react';
import './Header.css';

const Header = ({ title }) => {
  // Aktuelle Kalenderwoche berechnen
  const getCurrentWeek = () => {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 1);
    const diff = now - start;
    const oneWeek = 1000 * 60 * 60 * 24 * 7;
    return Math.ceil(diff / oneWeek);
  };

  const currentWeek = getCurrentWeek();
  const currentYear = new Date().getFullYear();

  return (
    <header className="header">
      <div className="header-left">
        <h2 className="header-title">{title}</h2>
      </div>

      <div className="header-right">
        <div className="header-week">
          <span className="header-week-label">Aktuelle Woche:</span>
          <span className="header-week-value">KW {currentWeek}/{currentYear}</span>
        </div>

        <button className="header-icon-btn" title="Benachrichtigungen">
          <Bell size={20} />
        </button>

        <button className="header-icon-btn" title="Benutzerprofil">
          <User size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;
