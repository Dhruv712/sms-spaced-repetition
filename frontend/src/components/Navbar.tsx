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
    <nav className="bg-gray-100 p-4 shadow-md mb-4">
      <div className="container mx-auto flex justify-between items-center">
        <ul className="flex space-x-4">
          {user ? (
            <>
              <li>
                <Link to="/" className="text-blue-600 hover:underline">Flashcards</Link>
              </li>
              <li>
                <Link to="/profile" className="text-blue-600 hover:underline">Profile</Link>
              </li>
              <li>
                <Link to="/history" className="text-blue-600 hover:underline">Review History</Link>
              </li>
              <li>
                <Link to="/manual-review" className="text-blue-600 hover:underline">Manual review</Link>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login" className="text-blue-600 hover:underline">Login</Link>
              </li>
              <li>
                <Link to="/register" className="text-blue-600 hover:underline">Register</Link>
              </li>
            </>
          )}
        </ul>
        {user && (
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">{user.email}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
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
