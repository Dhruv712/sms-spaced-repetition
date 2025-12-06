import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ProfileDropdown from './ProfileDropdown';

const Navbar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);
  
  useEffect(() => {
    // On mount, set dark mode from localStorage
    const stored = localStorage.getItem('darkMode');
    if (stored) {
      setDarkMode(stored === 'true');
      document.body.classList.toggle('dark', stored === 'true');
    }
  }, []);

  // Don't show navbar on landing page - must be after all hooks
  if (location.pathname === '/') {
    return null;
  }

  const toggleDarkMode = () => {
    setDarkMode((prev) => {
      const newMode = !prev;
      document.body.classList.toggle('dark', newMode);
      localStorage.setItem('darkMode', newMode.toString());
      return newMode;
    });
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <nav className="bg-gray-100 dark:bg-darksurface p-4 shadow-md dark:shadow-lg mb-4">
      <div className="w-full max-w-full px-4 flex justify-between items-center gap-4">
        {/* Logo/Brand */}
        <div className="flex items-center flex-shrink-0">
          <Link to="/dashboard" className="text-xl font-bold text-accent dark:text-accent">
            Cue
          </Link>
        </div>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center gap-4 flex-1 justify-center min-w-0">
          <ul className="flex space-x-6 items-center">
            {user ? (
              <>
                <li>
                  <Link to="/dashboard" className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-3 py-1.5 rounded-md transition-all duration-200">Dashboard</Link>
                </li>
                <li>
                  <Link to="/decks" className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-3 py-1.5 rounded-md transition-all duration-200">Decks</Link>
                </li>
                <li>
                  <Link to="/history" className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-3 py-1.5 rounded-md transition-all duration-200">Review History</Link>
                </li>
                <li>
                  <Link to="/review-due-cards" className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-3 py-1.5 rounded-md transition-all duration-200">Review Due Cards</Link>
                </li>
                {user.is_admin && (
                  <li>
                    <Link to="/admin" className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-3 py-1.5 rounded-md transition-all duration-200">Admin</Link>
                  </li>
                )}
              </>
            ) : (
              <>
                <li>
                  <Link to="/login" className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-3 py-1.5 rounded-md transition-all duration-200">Login</Link>
                </li>
                <li>
                  <Link to="/register" className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-3 py-1.5 rounded-md transition-all duration-200">Register</Link>
                </li>
              </>
            )}
          </ul>
          <div className="flex items-center space-x-3 flex-shrink-0">
            {user && (
              <>
                {!user.is_premium ? (
                  <Link
                    to="/premium"
                    className="px-4 py-2 bg-accent hover:bg-accent/90 text-white rounded-lg text-sm font-medium whitespace-nowrap transition-colors duration-200"
                  >
                    Get Premium
                  </Link>
                ) : (
                  <Link
                    to="/premium"
                    className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 px-3 py-1.5 text-sm font-light whitespace-nowrap transition-colors duration-200"
                  >
                    Premium
                  </Link>
                )}
              </>
            )}
            {/* Dark mode toggle button */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 flex-shrink-0"
              title="Toggle dark mode"
            >
              {darkMode ? (
                <span role="img" aria-label="Light mode">🌞</span>
              ) : (
                <span role="img" aria-label="Dark mode">🌙</span>
              )}
            </button>
            {user && <ProfileDropdown />}
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center space-x-2">
          {/* Dark mode toggle for mobile */}
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200"
            title="Toggle dark mode"
          >
            {darkMode ? (
              <span role="img" aria-label="Light mode">🌞</span>
            ) : (
              <span role="img" aria-label="Dark mode">🌙</span>
            )}
          </button>
          
          {/* Hamburger Menu Button */}
          <button
            onClick={toggleMenu}
            className="p-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200"
            aria-label="Toggle menu"
          >
            <div className="w-6 h-6 flex flex-col justify-center items-center">
              <span className={`block w-5 h-0.5 bg-gray-600 dark:bg-gray-300 transition-all duration-300 ${isMenuOpen ? 'rotate-45 translate-y-1' : ''}`}></span>
              <span className={`block w-5 h-0.5 bg-gray-600 dark:bg-gray-300 transition-all duration-300 mt-1 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
              <span className={`block w-5 h-0.5 bg-gray-600 dark:bg-gray-300 transition-all duration-300 mt-1 ${isMenuOpen ? '-rotate-45 -translate-y-1' : ''}`}></span>
            </div>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden mt-4 pb-4 border-t border-gray-200 dark:border-gray-700">
          <div className="pt-4 space-y-2">
            {user ? (
              <>
                <Link 
                  to="/dashboard" 
                  onClick={closeMenu}
                  className="block px-4 py-2 text-accent dark:text-accent hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                >
                  Dashboard
                </Link>
                <Link 
                  to="/decks" 
                  onClick={closeMenu}
                  className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                >
                  Decks
                </Link>
                <Link 
                  to="/history" 
                  onClick={closeMenu}
                  className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                >
                  Review History
                </Link>
                <Link 
                  to="/review-due-cards" 
                  onClick={closeMenu}
                  className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                >
                  Review Due Cards
                </Link>
                {user.is_admin && (
                  <Link 
                    to="/admin" 
                    onClick={closeMenu}
                    className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                  >
                    Admin
                  </Link>
                )}
                {!user.is_premium && (
                  <Link 
                    to="/premium" 
                    onClick={closeMenu}
                    className="block px-4 py-2 bg-accent hover:bg-accent/90 text-white rounded-lg transition-colors duration-200 font-medium text-center"
                  >
                    Get Premium
                  </Link>
                )}
                {user.is_premium && (
                  <Link 
                    to="/premium" 
                    onClick={closeMenu}
                    className="block px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200 text-center"
                  >
                    Premium
                  </Link>
                )}
                <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
                  <ProfileDropdown />
                </div>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  onClick={closeMenu}
                  className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                >
                  Login
                </Link>
                <Link 
                  to="/register" 
                  onClick={closeMenu}
                  className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
