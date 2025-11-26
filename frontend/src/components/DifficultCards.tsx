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
      
      <div className="space-y-4">
        {difficultCards.map((card, index) => (
          <div
            key={card.flashcard_id}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-primary-300 dark:hover:border-primary-600 transition-colors duration-200"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                    #{index + 1}
                  </span>
                  {card.deck_name && (
                    <span className="inline-block px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded">
                      {card.deck_name}
                    </span>
                  )}
                </div>
                <h3 className="text-base font-medium text-gray-900 dark:text-darktext mb-2">
                  {card.concept}
                </h3>
              </div>
              <div className="text-right ml-4">
                <div className="text-2xl font-light text-red-600 dark:text-red-400">
                  {card.accuracy.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {card.correct_reviews}/{card.total_reviews} correct
                </div>
              </div>
            </div>
            
            <button
              onClick={() => setExpandedCard(expandedCard === card.flashcard_id ? null : card.flashcard_id)}
              className="text-xs text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors duration-200"
            >
              {expandedCard === card.flashcard_id ? 'Hide answer' : 'Show answer'}
            </button>
            
            {expandedCard === card.flashcard_id && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Correct Answer:</div>
                <div className="prose prose-sm max-w-none text-gray-700 dark:text-gray-300">
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

