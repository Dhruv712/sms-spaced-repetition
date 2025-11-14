import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';

interface AnkiImportProps {
  onSuccess?: () => void;
}

interface Deck {
  id: number;
  name: string;
}

const AnkiImport: React.FC<AnkiImportProps> = ({ onSuccess }) => {
  const { token, user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [deckId, setDeckId] = useState<number | null>(null);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const fetchDecks = async () => {
      if (!token) return;
      try {
        const response = await axios.get(buildApiUrl('/decks/'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        setDecks(response.data);
      } catch (err) {
        console.error('Error fetching decks:', err);
      }
    };
    fetchDecks();
  }, [token]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setSuccess(null);
    }
  };

  const handleImport = async () => {
    if (!file || !token) {
      setError('Please select an .apkg or .txt file');
      return;
    }

    if (!user?.is_premium) {
      setError('Anki import is a premium feature. Please upgrade to Premium.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (deckId) {
        formData.append('deck_id', deckId.toString());
      }

      const response = await axios.post(
        buildApiUrl('/anki/import'),
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setSuccess(`Successfully imported ${response.data.created_count} flashcards${deckId ? '' : ` into new deck "${response.data.deck_name}"`}`);
      setFile(null);
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import Anki deck. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user?.is_premium) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Import Anki Deck</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Anki deck import is a premium feature. Upgrade to Premium to import your Anki decks.
        </p>
        <a
          href="/premium"
          className="inline-block px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors duration-200 text-sm"
        >
          Upgrade to Premium
        </a>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Import Anki Deck</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-sm text-red-800 dark:text-red-300">
          {error}
        </div>
      )}
      
      {success && (
        <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded text-sm text-green-800 dark:text-green-300">
          {success}
        </div>
      )}

      <div className="space-y-4">
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded text-sm text-blue-800 dark:text-blue-300">
          <p className="font-medium mb-1">Export Options:</p>
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li><strong>Recommended:</strong> Export as "Notes in Plain Text" (.txt) from Anki</li>
            <li>Or export as "Anki Deck Package" (.apkg)</li>
          </ul>
          <p className="mt-2 text-xs">In Anki: File → Export → Select format → Choose your deck → Export</p>
        </div>

        <div>
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">
            Select .apkg or .txt file
          </label>
          <input
            type="file"
            accept=".apkg,.txt"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 dark:text-gray-400
              file:mr-4 file:py-2 file:px-4
              file:rounded file:border-0
              file:text-sm file:font-medium
              file:bg-primary-50 file:text-primary-700
              hover:file:bg-primary-100
              dark:file:bg-primary-900 dark:file:text-primary-300"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">
            Import to existing deck (optional)
          </label>
          <select
            value={deckId || ''}
            onChange={(e) => setDeckId(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-darktext text-sm"
          >
            <option value="">Create new deck</option>
            {decks.map((deck) => (
              <option key={deck.id} value={deck.id}>
                {deck.name}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleImport}
          disabled={loading || !file}
          className="w-full px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 text-sm"
        >
          {loading ? 'Importing...' : 'Import Deck'}
        </button>
      </div>
    </div>
  );
};

export default AnkiImport;

