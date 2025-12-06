import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { buildApiUrl } from '../config';
import SmsSetupBanner from '../components/SmsSetupBanner';
import { getOnboardingState, setOnboardingState, markOnboardingCompleted } from '../utils/onboarding';
import NewContentModal from '../components/NewContentModal';
import NewFlashcardModal from '../components/NewFlashcardModal';
import NewDeckModal from '../components/NewDeckModal';
import ViewDeckCardsModal from '../components/ViewDeckCardsModal';

interface Deck {
  id: number;
  name: string;
  flashcards_count: number;
  created_at: string;
  image_url?: string;
  sms_enabled?: boolean;
}

const DecksPage: React.FC = () => {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploadingImage, setUploadingImage] = useState<number | null>(null);
  const [togglingSms, setTogglingSms] = useState<number | null>(null);
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const fileInputRefs = useRef<{ [key: number]: HTMLInputElement | null }>({});
  const [onboardingStep, setOnboardingStep] = useState<number>(0);
  const [showNewContentModal, setShowNewContentModal] = useState(false);
  const [showFlashcardModal, setShowFlashcardModal] = useState(false);
  const [showDeckModal, setShowDeckModal] = useState(false);
  const [showViewCardsModal, setShowViewCardsModal] = useState(false);
  const [viewingDeckId, setViewingDeckId] = useState<number | null>(null);
  const [viewingDeckName, setViewingDeckName] = useState<string>('');
  const [preselectedDeckId, setPreselectedDeckId] = useState<number | null>(null);

  const fetchDecks = useCallback(async () => {
    if (!token) {
      setError('Authentication token not found.');
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.get(buildApiUrl('/decks/'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      console.log('Fetched decks:', response.data);
      setDecks(response.data);
    } catch (err) {
      console.error('Error fetching decks:', err);
      setError('Failed to load decks. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchDecks();
  }, [fetchDecks]);

  // Onboarding: Step 2 (Decks) - was Step 3 before removing Flashcards step
  useEffect(() => {
    if (!user) return;
    const state = getOnboardingState(user.email);
    if (state.completed) {
      setOnboardingStep(0);
      return;
    }
    if (state.step === 2) {
      setOnboardingStep(2);
    } else {
      setOnboardingStep(0);
    }
  }, [user]);

  const handleOnboardingSkip = () => {
    if (!user) return;
    markOnboardingCompleted(user.email);
    setOnboardingStep(0);
  };

  const handleOnboardingNextFromDecks = () => {
    if (!user) return;
    setOnboardingState(user.email, { step: 3, completed: false }); // Step 3 is now Profile (was Step 4)
    setOnboardingStep(0);
    navigate('/profile');
  };


  const handleDeleteDeck = async (deckId: number) => {
    if (!token) return;

    // Ask user what they want to do with the cards
    const deleteCards = window.confirm(
      'Do you want to delete all flashcards in this deck?\n\n' +
      'Click OK to delete the deck AND all its flashcards.\n' +
      'Click Cancel to delete the deck but keep the flashcards (they will be unassigned).'
    );

    setIsLoading(true); // Set loading to true while deleting
    setError('');
    try {
      const response = await axios.delete(buildApiUrl(`/decks/${deckId}?delete_cards=${deleteCards}`), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      setDecks(prevDecks => prevDecks.filter(deck => deck.id !== deckId));
      // Show success message
      if (response.data?.message) {
        alert(response.data.message);
      }
    } catch (err) {
      console.error('Error deleting deck:', err);
      setError('Failed to delete deck. Please try again.');
    } finally {
      setIsLoading(false); // Reset loading
    }
  };

  const handleImageUpload = async (deckId: number, file: File) => {
    if (!token) return;

    setUploadingImage(deckId);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        buildApiUrl(`/decks/upload-image/${deckId}`),
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Update the deck in the local state
      setDecks(prevDecks =>
        prevDecks.map(deck =>
          deck.id === deckId
            ? { ...deck, image_url: response.data.image_url }
            : deck
        )
      );
      console.log('Image upload successful:', response.data.image_url);
    } catch (err) {
      console.error('Error uploading image:', err);
      setError('Failed to upload image. Please try again.');
    } finally {
      setUploadingImage(null);
    }
  };

  const triggerFileInput = (deckId: number) => {
    if (fileInputRefs.current[deckId]) {
      fileInputRefs.current[deckId]?.click();
    }
  };

  const handleFileSelect = (deckId: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleImageUpload(deckId, file);
    }
  };

  const handleToggleSms = async (deckId: number, currentStatus: boolean) => {
    if (!token || togglingSms === deckId) return;

    setTogglingSms(deckId);
    setError('');
    try {
      const response = await axios.put(
        buildApiUrl(`/decks/${deckId}/sms`),
        { sms_enabled: !currentStatus },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      // Update the deck in the local state
      setDecks(prevDecks =>
        prevDecks.map(deck =>
          deck.id === deckId
            ? { ...deck, sms_enabled: response.data.sms_enabled }
            : deck
        )
      );
      console.log('SMS toggle successful:', response.data);
    } catch (err) {
      console.error('Error toggling SMS:', err);
      setError('Failed to toggle SMS setting. Please try again.');
    } finally {
      setTogglingSms(null);
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
        {onboardingStep === 2 && (
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <p className="text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-wide mb-1">
                  Step 2 of 3
                </p>
                <h2 className="text-sm font-medium text-gray-900 dark:text-darktext mb-1">
                  Create decks and flashcards
                </h2>
                <p className="text-xs text-gray-700 dark:text-gray-300">
                  Click "New" to create decks and flashcards. Turn on SMS for decks you want Cue to text you from.
                </p>
              </div>
              <div className="flex items-center gap-2 self-end md:self-auto">
                <button
                  type="button"
                  onClick={handleOnboardingSkip}
                  className="px-3 py-1.5 text-xs rounded border border-transparent text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100"
                >
                  Skip tour
                </button>
                <button
                  type="button"
                  onClick={handleOnboardingNextFromDecks}
                  className="px-3 py-1.5 text-xs rounded bg-primary-600 text-white hover:bg-primary-700 transition-colors duration-200"
                >
                  Next: Set up SMS & profile
                </button>
              </div>
            </div>
          </div>
        )}
        {/* SMS Setup Banner */}
        <SmsSetupBanner />
        
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
              Your Flashcard Decks
            </h1>
            <p className="mt-2 text-secondary-600 dark:text-secondary-400">
              Organize your flashcards into custom collections.
            </p>
          </div>
          <button
            onClick={() => setShowNewContentModal(true)}
            className="px-6 py-3 bg-accent hover:bg-accent/90 text-white rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New
          </button>
        </div>

        <div className="bg-white dark:bg-secondary-800 rounded-lg shadow-soft p-6">
          <h2 className="text-xl font-semibold text-secondary-900 dark:text-white mb-4">My Decks</h2>
          {decks.length === 0 ? (
            <p className="text-secondary-600 dark:text-secondary-400">No decks created yet. Create one above!</p>
          ) : (
            <div className="space-y-4">
              {decks.map(deck => (
                <div key={deck.id} className="p-4 border border-secondary-200 dark:border-secondary-700 rounded-lg flex justify-between items-center bg-secondary-50 dark:bg-secondary-900/20">
                  <div className="flex items-center space-x-4">
                    {/* Deck Preview Image */}
                    <div className="relative">
                      <img
                        src={deck.image_url || "/cue_default_image.jpeg"}
                        alt={`${deck.name} preview`}
                        className="w-16 h-16 rounded-lg object-cover border border-secondary-200 dark:border-secondary-600"
                        onError={(e) => {
                          console.error('Image failed to load:', deck.image_url);
                          e.currentTarget.src = "/cue_default_image.jpeg";
                        }}
                      />
                      <button
                        onClick={() => triggerFileInput(deck.id)}
                        disabled={uploadingImage === deck.id}
                        className="absolute -bottom-1 -right-1 bg-primary-600 hover:bg-primary-700 text-white rounded-full p-1 text-xs transition-colors duration-200 disabled:opacity-50"
                        title="Upload preview image"
                      >
                        {uploadingImage === deck.id ? (
                          <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          "📷"
                        )}
                      </button>
                      <input
                        ref={(el) => { fileInputRefs.current[deck.id] = el; }}
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleFileSelect(deck.id, e)}
                        className="hidden"
                      />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-secondary-900 dark:text-white">
                        {deck.name} ({deck.flashcards_count || 0} cards
                        {!user?.is_premium && (
                          <span className="text-sm font-normal text-secondary-500 dark:text-secondary-400">
                            {' '}/ 20 max
                          </span>
                        )}
                        )
                      </h3>
                      <p className="text-sm text-secondary-500 dark:text-secondary-400">Created: {new Date(deck.created_at).toLocaleDateString()}</p>
                      {!user?.is_premium && deck.flashcards_count >= 20 && (
                        <p className="text-xs text-red-600 dark:text-red-400 mt-1">Free tier limit reached - upgrade for unlimited</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {/* SMS Toggle */}
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs font-medium ${deck.sms_enabled ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'}`}>
                        {deck.sms_enabled ? '📱 SMS On' : '🔇 SMS Muted'}
                      </span>
                      <button
                        onClick={() => handleToggleSms(deck.id, deck.sms_enabled || false)}
                        disabled={togglingSms === deck.id}
                        className={`relative inline-flex h-6 w-12 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                          deck.sms_enabled 
                            ? 'bg-primary-600' 
                            : 'bg-gray-300 dark:bg-gray-600'
                        } ${togglingSms === deck.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                        title={deck.sms_enabled ? 'Disable SMS for this deck' : 'Enable SMS for this deck'}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                            deck.sms_enabled ? 'translate-x-7' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>
                    <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setViewingDeckId(deck.id);
                        setViewingDeckName(deck.name);
                        setShowViewCardsModal(true);
                      }}
                      className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 text-sm font-medium"
                    >
                      View Cards
                    </button>
                    <button
                      onClick={() => handleDeleteDeck(deck.id)}
                      className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium"
                    >
                      Delete
                    </button>
                    <button
                      className="review-deck-btn"
                      onClick={() => navigate(`/decks/${deck.id}/review`)}
                    >
                      Review Deck
                    </button>
                    <button
                      onClick={() => navigate(`/decks/${deck.id}/mastery`)}
                      className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 text-sm font-medium"
                    >
                      Mastery Graph
                    </button>
                  </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modals */}
        <NewContentModal
          isOpen={showNewContentModal}
          onClose={() => setShowNewContentModal(false)}
          onSelectFlashcards={() => {
            setShowNewContentModal(false);
            setPreselectedDeckId(null);
            setShowFlashcardModal(true);
          }}
          onSelectDeck={() => {
            setShowNewContentModal(false);
            setShowDeckModal(true);
          }}
        />

        <NewFlashcardModal
          isOpen={showFlashcardModal}
          onClose={() => {
            setShowFlashcardModal(false);
            setPreselectedDeckId(null);
          }}
          onSuccess={fetchDecks}
          preselectedDeckId={preselectedDeckId}
        />

        <NewDeckModal
          isOpen={showDeckModal}
          onClose={() => setShowDeckModal(false)}
          onDeckCreated={(deckId) => {
            setPreselectedDeckId(deckId);
            setShowFlashcardModal(true);
          }}
          onSuccess={fetchDecks}
        />

        {viewingDeckId && (
          <ViewDeckCardsModal
            isOpen={showViewCardsModal}
            onClose={() => {
              setShowViewCardsModal(false);
              setViewingDeckId(null);
              setViewingDeckName('');
            }}
            deckId={viewingDeckId}
            deckName={viewingDeckName}
            onSuccess={fetchDecks}
          />
        )}
      </div>
    </div>
  );
};

export default DecksPage; 