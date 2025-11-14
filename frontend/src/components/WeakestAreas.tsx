import React from 'react';

interface WeakestAreasProps {
  stats: any;
}

const WeakestAreas: React.FC<WeakestAreasProps> = ({ stats }) => {
  const weakestTags = stats?.weakest_areas?.tags || [];
  const weakestDecks = stats?.weakest_areas?.decks || [];

  if (weakestTags.length === 0 && weakestDecks.length === 0) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Weakest Areas</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Not enough review data yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-6">Weakest Areas</h2>
      
      {weakestTags.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Tags</h3>
          <div className="space-y-2">
            {weakestTags.slice(0, 5).map((item: any, index: number) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                <span className="text-sm text-gray-900 dark:text-darktext">{item.tag}</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {item.accuracy.toFixed(1)}% ({item.review_count} reviews)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {weakestDecks.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Decks</h3>
          <div className="space-y-2">
            {weakestDecks.slice(0, 5).map((item: any, index: number) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                <span className="text-sm text-gray-900 dark:text-darktext">{item.deck_name}</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {item.accuracy.toFixed(1)}% ({item.review_count} reviews)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WeakestAreas;

