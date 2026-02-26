import Sidebar from './Sidebar';
import Header from './Header';
import './Layout.css';

const Layout = ({ children, title }) => {
  return (
    <div className="layout">
      <Sidebar />
      <div className="layout-main">
        <Header title={title} />
        <main className="layout-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
