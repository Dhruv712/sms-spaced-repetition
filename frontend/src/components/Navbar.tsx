import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-gray-100 p-4 shadow-md mb-4">
      <ul className="flex space-x-4">
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
      </ul>
    </nav>
  );
};

export default Navbar;
