import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

interface Deck {
  id: number;
  name: string;
  flashcards_count: number;
  created_at: string;
}

const DecksPage: React.FC = () => {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [newDeckName, setNewDeckName] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [creatingDeck, setCreatingDeck] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    fetchDecks();
  }, [token]);

  const fetchDecks = async () => {
    if (!token) {
      setError('Authentication token not found.');
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.get('http://localhost:8000/decks/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setDecks(response.data);
    } catch (err) {
      console.error('Error fetching decks:', err);
      setError('Failed to load decks. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateDeck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDeckName.trim() || !token || creatingDeck) return;

    setCreatingDeck(true);
    setError('');
    try {
      const response = await axios.post(
        'http://localhost:8000/decks/',
        { name: newDeckName },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      setDecks(prevDecks => [...prevDecks, response.data]);
      setNewDeckName('');
    } catch (err) {
      console.error('Error creating deck:', err);
      setError('Failed to create deck. Please try again.');
    } finally {
      setCreatingDeck(false);
    }
  };

  const handleDeleteDeck = async (deckId: number) => {
    if (!token || !window.confirm('Are you sure you want to delete this deck? All flashcards in this deck will be unassigned.')) return;

    setIsLoading(true); // Set loading to true while deleting
    setError('');
    try {
      await axios.delete(`http://localhost:8000/decks/${deckId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setDecks(prevDecks => prevDecks.filter(deck => deck.id !== deckId));
    } catch (err) {
      console.error('Error deleting deck:', err);
      setError('Failed to delete deck. Please try again.');
    } finally {
      setIsLoading(false); // Reset loading
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 flex items-center justify-center">
        <div className="text-xl text-red-600 dark:text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
            Your Flashcard Decks
          </h1>
          <p className="mt-2 text-secondary-600 dark:text-secondary-400">
            Organize your flashcards into custom collections.
          </p>
        </div>

        <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6 mb-8">
          <h2 className="text-xl font-semibold text-secondary-900 dark:text-white mb-4">Create New Deck</h2>
          <form onSubmit={handleCreateDeck} className="flex space-x-4">
            <input
              type="text"
              placeholder="Deck Name"
              value={newDeckName}
              onChange={(e) => setNewDeckName(e.target.value)}
              className="flex-grow block w-full rounded-md border-secondary-300 dark:border-secondary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-secondary-700 dark:text-white sm:text-sm"
              required
            />
            <button
              type="submit"
              disabled={creatingDeck}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {creatingDeck ? 'Creating...' : 'Create Deck'}
            </button>
          </form>
        </div>

        <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6">
          <h2 className="text-xl font-semibold text-secondary-900 dark:text-white mb-4">My Decks</h2>
          {decks.length === 0 ? (
            <p className="text-secondary-600 dark:text-secondary-400">No decks created yet. Create one above!</p>
          ) : (
            <div className="space-y-4">
              {decks.map(deck => (
                <div key={deck.id} className="p-4 border border-secondary-200 dark:border-secondary-700 rounded-lg flex justify-between items-center bg-secondary-50 dark:bg-secondary-900/20">
                  <div>
                    <h3 className="text-lg font-medium text-secondary-900 dark:text-white">{deck.name} ({deck.flashcards_count || 0} cards)</h3>
                    <p className="text-sm text-secondary-500 dark:text-secondary-400">Created: {new Date(deck.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex space-x-2">
                    <Link
                      to={`/flashcards?deckId=${deck.id}`}
                      className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 text-sm font-medium"
                    >
                      View Cards
                    </Link>
                    <button
                      onClick={() => handleDeleteDeck(deck.id)}
                      className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DecksPage; 