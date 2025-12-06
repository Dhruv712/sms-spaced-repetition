import React from 'react';

interface NewContentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectFlashcards: () => void;
  onSelectDeck: () => void;
}

const NewContentModal: React.FC<NewContentModalProps> = ({
  isOpen,
  onClose,
  onSelectFlashcards,
  onSelectDeck,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 dark:bg-opacity-70">
      <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-8 max-w-md w-full mx-4 border border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-darktext">Create New</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-4">
          <button
            onClick={onSelectFlashcards}
            className="w-full px-6 py-4 bg-accent hover:bg-accent/90 text-white rounded-lg font-medium transition-colors duration-200 text-left flex items-center justify-between"
          >
            <span>New flashcard(s)</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            onClick={onSelectDeck}
            className="w-full px-6 py-4 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-darktext rounded-lg font-medium transition-colors duration-200 text-left flex items-center justify-between"
          >
            <span>New deck</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewContentModal;

