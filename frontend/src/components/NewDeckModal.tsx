import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import PdfImport from './PdfImport';
import AnkiImport from './AnkiImport';

interface NewDeckModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDeckCreated: (deckId: number) => void;
  onSuccess: () => void;
}

type DeckMode = 'select' | 'scratch' | 'pdf' | 'anki';

const NewDeckModal: React.FC<NewDeckModalProps> = ({
  isOpen,
  onClose,
  onDeckCreated,
  onSuccess,
}) => {
  const [mode, setMode] = useState<DeckMode>('select');
  const [deckName, setDeckName] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const { token } = useAuth();

  const handleCreateFromScratch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!deckName.trim() || !token || creating) return;

    setCreating(true);
    setError('');

    try {
      const response = await axios.post(
        buildApiUrl('/decks/'),
        { name: deckName.trim() },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      const newDeckId = response.data.id;
      onSuccess();
      onDeckCreated(newDeckId);
      onClose();
    } catch (err: any) {
      console.error('Error creating deck:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to create deck. Please try again.';
      setError(errorMessage);
    } finally {
      setCreating(false);
    }
  };

  const handleImportSuccess = () => {
    onSuccess();
    onClose();
  };

  const resetModal = useCallback(() => {
    setMode('select');
    setDeckName('');
    setError('');
    setCreating(false);
  }, []);

  React.useEffect(() => {
    if (!isOpen) {
      resetModal();
    }
  }, [isOpen, resetModal]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 dark:bg-opacity-70 overflow-y-auto">
      <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 my-8 border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-darktext">Create New Deck</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 rounded">
            {error}
          </div>
        )}

        {mode === 'select' && (
          <div className="space-y-4">
            <button
              onClick={() => setMode('scratch')}
              className="w-full px-6 py-4 bg-accent hover:bg-accent/90 text-white rounded-lg font-medium transition-colors duration-200 text-left flex items-center justify-between"
            >
              <span>From scratch</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <button
              onClick={() => setMode('pdf')}
              className="w-full px-6 py-4 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-darktext rounded-lg font-medium transition-colors duration-200 text-left flex items-center justify-between"
            >
              <span>From PDF</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <button
              onClick={() => setMode('anki')}
              className="w-full px-6 py-4 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-darktext rounded-lg font-medium transition-colors duration-200 text-left flex items-center justify-between"
            >
              <span>From Anki deck</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {mode === 'scratch' && (
          <form onSubmit={handleCreateFromScratch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Deck Name
              </label>
              <input
                type="text"
                placeholder="Enter deck name"
                value={deckName}
                onChange={(e) => setDeckName(e.target.value)}
                required
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext dark:border-gray-600"
                autoFocus
              />
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setMode('select')}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={creating || !deckName.trim()}
                className="flex-1 px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90 disabled:opacity-50 transition-colors"
              >
                {creating ? 'Creating...' : 'Create Deck'}
              </button>
            </div>
          </form>
        )}

        {mode === 'pdf' && (
          <div className="space-y-4">
            <button
              onClick={() => setMode('select')}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              ← Back
            </button>
            <PdfImport onSuccess={handleImportSuccess} />
          </div>
        )}

        {mode === 'anki' && (
          <div className="space-y-4">
            <button
              onClick={() => setMode('select')}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              ← Back
            </button>
            <AnkiImport onSuccess={handleImportSuccess} />
          </div>
        )}
      </div>
    </div>
  );
};

export default NewDeckModal;

