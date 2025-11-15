import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';

interface PdfImportProps {
  onSuccess?: () => void;
}

interface Deck {
  id: number;
  name: string;
}

const PdfImport: React.FC<PdfImportProps> = ({ onSuccess }) => {
  const { token, user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [instructions, setInstructions] = useState('');
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
      setError('Please select a PDF file');
      return;
    }

    if (!user?.is_premium) {
      setError('PDF import is a premium feature. Please upgrade to Premium.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('instructions', instructions);
      if (deckId) {
        formData.append('deck_id', deckId.toString());
      }

      const response = await axios.post(
        buildApiUrl('/pdf/import'),
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setSuccess(`Successfully created ${response.data.created_count} flashcards${deckId ? '' : ` in new deck "${response.data.deck_name}"`}`);
      setFile(null);
      setInstructions('');
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user?.is_premium) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6 mb-8">
        <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Create Flashcards from PDF</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          PDF import is a premium feature. Upgrade to Premium to create flashcards from PDF documents.
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
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6 mb-8">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Create Flashcards from PDF</h2>
      
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
        <div>
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">
            Select PDF file
          </label>
          <input
            type="file"
            accept=".pdf"
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
            Instructions (optional)
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="e.g., 'Focus on key concepts from chapters 1-3', 'Create cards for definitions only', 'Make 20-30 cards'"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-darktext text-sm"
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Provide specific instructions for how to create flashcards from the PDF. Leave empty for default behavior.
          </p>
        </div>

        <div>
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">
            Add to existing deck (optional)
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
          {loading ? 'Processing... this could take a couple minutes' : 'Create Flashcards'}
        </button>
      </div>
    </div>
  );
};

export default PdfImport;

