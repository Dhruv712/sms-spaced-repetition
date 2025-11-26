import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface DifficultCard {
  flashcard_id: number;
  concept: string;
  definition: string;
  accuracy: number;
  total_reviews: number;
  correct_reviews: number;
  deck_id: number | null;
  deck_name: string | null;
}

const DifficultCards: React.FC = () => {
  const { token } = useAuth();
  const [difficultCards, setDifficultCards] = useState<DifficultCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedCard, setExpandedCard] = useState<number | null>(null);

  useEffect(() => {
    if (!token) return;

    const fetchDifficultCards = async () => {
      try {
        const response = await axios.get(buildApiUrl('/dashboard/difficult-cards'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        setDifficultCards(response.data.difficult_cards || []);
      } catch (err) {
        console.error('Error fetching difficult cards:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDifficultCards();
  }, [token]);

  if (loading) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (difficultCards.length === 0) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Most Difficult Cards</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No cards with enough reviews yet. Review more cards to see difficulty analysis.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Most Difficult Cards</h2>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-6">
        Cards with the lowest accuracy (minimum 3 reviews)
      </p>
      
      <div className="space-y-2">
        {difficultCards.map((card, index) => (
          <div
            key={card.flashcard_id}
            className="border border-gray-200 dark:border-gray-700 rounded p-3 hover:border-primary-300 dark:hover:border-primary-600 transition-colors duration-200"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                    #{index + 1}
                  </span>
                  {card.deck_name && (
                    <span className="inline-block px-1.5 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded">
                      {card.deck_name}
                    </span>
                  )}
                </div>
                <h3 className="text-sm font-medium text-gray-900 dark:text-darktext mb-1 truncate">
                  {card.concept}
                </h3>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {card.correct_reviews}/{card.total_reviews} correct
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <div className="text-xl font-light text-red-600 dark:text-red-400">
                  {card.accuracy.toFixed(1)}%
                </div>
                <button
                  onClick={() => setExpandedCard(expandedCard === card.flashcard_id ? null : card.flashcard_id)}
                  className="text-xs text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors duration-200 whitespace-nowrap"
                >
                  {expandedCard === card.flashcard_id ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>
            
            {expandedCard === card.flashcard_id && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Correct:</div>
                <div className="prose prose-xs max-w-none text-gray-700 dark:text-gray-300 text-xs">
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {card.definition}
                  </ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DifficultCards;

