import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface IncorrectAnswer {
  answer: string;
  count: number;
}

interface ConfusionCard {
  flashcard_id: number;
  concept: string;
  definition: string;
  deck_id: number | null;
  deck_name: string | null;
  incorrect_answers: IncorrectAnswer[];
  total_incorrect: number;
}

const ConfusionBreakdown: React.FC = () => {
  const { token } = useAuth();
  const [confusionData, setConfusionData] = useState<ConfusionCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedCard, setExpandedCard] = useState<number | null>(null);

  useEffect(() => {
    if (!token) return;

    const fetchConfusionBreakdown = async () => {
      try {
        const response = await axios.get(buildApiUrl('/dashboard/confusion-breakdown'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        setConfusionData(response.data.confusion_breakdown || []);
      } catch (err) {
        console.error('Error fetching confusion breakdown:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchConfusionBreakdown();
  }, [token]);

  if (loading) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (confusionData.length === 0) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Confusion Breakdown</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No incorrect answers tracked yet. Keep reviewing to see which answers you confuse most often.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Confusion Breakdown</h2>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-6">
        Cards where you frequently type the same incorrect answer
      </p>
      
      <div className="space-y-2">
        {confusionData.map((card) => (
          <div
            key={card.flashcard_id}
            className="border border-gray-200 dark:border-gray-700 rounded p-3 hover:border-primary-300 dark:hover:border-primary-600 transition-colors duration-200"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  {card.deck_name && (
                    <span className="inline-block px-1.5 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded">
                      {card.deck_name}
                    </span>
                  )}
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {card.total_incorrect}×
                  </span>
                </div>
                <h3 className="text-sm font-medium text-gray-900 dark:text-darktext mb-1.5 truncate">
                  {card.concept}
                </h3>
                <div className="space-y-1">
                  {card.incorrect_answers.slice(0, 2).map((item, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="text-gray-600 dark:text-gray-400 truncate flex-1 mr-2">
                        "{item.answer}"
                      </span>
                      <span className="text-gray-500 dark:text-gray-500 font-medium whitespace-nowrap">
                        {item.count}×
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <button
                onClick={() => setExpandedCard(expandedCard === card.flashcard_id ? null : card.flashcard_id)}
                className="text-xs text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors duration-200 whitespace-nowrap"
              >
                {expandedCard === card.flashcard_id ? 'Hide' : 'Show'}
              </button>
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

export default ConfusionBreakdown;

