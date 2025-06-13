import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-gray-100 dark:bg-darksurface p-4 shadow-md dark:shadow-lg mb-4">
      <div className="container mx-auto flex justify-between items-center">
        <ul className="flex space-x-4">
          {user ? (
            <>
              <li>
                <Link to="/" className="text-primary-600 dark:text-primary-300 hover:underline hover:text-primary-800 dark:hover:text-primary-100 transition-colors duration-200">Flashcards</Link>
              </li>
              <li>
                <Link to="/decks" className="text-primary-600 dark:text-primary-300 hover:underline hover:text-primary-800 dark:hover:text-primary-100 transition-colors duration-200">Decks</Link>
              </li>
              <li>
                <Link to="/profile" className="text-primary-600 dark:text-primary-300 hover:underline hover:text-primary-800 dark:hover:text-primary-100 transition-colors duration-200">Profile</Link>
              </li>
              <li>
                <Link to="/history" className="text-primary-600 dark:text-primary-300 hover:underline hover:text-primary-800 dark:hover:text-primary-100 transition-colors duration-200">Review History</Link>
              </li>
              <li>
                <Link to="/manual-review" className="text-primary-600 dark:text-primary-300 hover:underline hover:text-primary-800 dark:hover:text-primary-100 transition-colors duration-200">Manual review</Link>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login" className="text-primary-600 dark:text-primary-300 hover:underline hover:text-primary-800 dark:hover:text-primary-100 transition-colors duration-200">Login</Link>
              </li>
              <li>
                <Link to="/register" className="text-primary-600 dark:text-primary-300 hover:underline hover:text-primary-800 dark:hover:text-primary-100 transition-colors duration-200">Register</Link>
              </li>
            </>
          )}
        </ul>
        {user && (
          <div className="flex items-center space-x-4">
            <span className="text-gray-600 dark:text-gray-300">{user.email}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 transition-colors duration-200"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
