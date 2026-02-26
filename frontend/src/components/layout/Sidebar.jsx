import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Package, 
  ShoppingCart, 
  DollarSign, 
  Calendar, 
  Layers, 
  History, 
  Settings 
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/generator', icon: Package, label: 'Generator' },
    { path: '/artikel', icon: ShoppingCart, label: 'Artikel' },
    { path: '/preise', icon: DollarSign, label: 'Preise' },
    { path: '/wochenquelle', icon: Calendar, label: 'Wochenplanung' },
    { path: '/masterplaene', icon: Layers, label: 'Masterplaene' },
    { path: '/historie', icon: History, label: 'Historie' },
    { path: '/einstellungen', icon: Settings, label: 'Einstellungen' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">
          <span className="sidebar-logo">🥬</span>
          Paradieschen
        </h1>
        <p className="sidebar-subtitle">Kistengenerator</p>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <p className="sidebar-version">Version 1.0.0</p>
      </div>
    </aside>
  );
};

export default Sidebar;
