import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Welcome to SpacedText</h1>
      <p>This is your dashboard.</p>

      <ul>
        <li><Link to="/flashcards">View/Edit Flashcards</Link></li>
        {/* In future: Add Profile + Stats links here */}
      </ul>
    </div>
  );
};

export default Dashboard;
