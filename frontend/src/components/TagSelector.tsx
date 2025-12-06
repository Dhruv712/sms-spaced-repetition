import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';

interface TagSelectorProps {
  selectedTags: string[];
  onChange: (tags: string[]) => void;
  existingTags?: string[]; // Optional: if not provided, will fetch from API
}

const TagSelector: React.FC<TagSelectorProps> = ({ selectedTags, onChange, existingTags: providedTags }) => {
  const { token } = useAuth();
  const [availableTags, setAvailableTags] = useState<string[]>(providedTags || []);
  const [newTagInput, setNewTagInput] = useState('');
  const [showNewTagInput, setShowNewTagInput] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (providedTags) {
      setAvailableTags(providedTags);
      return;
    }

    // Fetch existing tags from user's flashcards
    const fetchTags = async () => {
      if (!token) return;
      try {
        const response = await axios.get(buildApiUrl('/flashcards/with-reviews'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        const allTags = new Set<string>();
        response.data.forEach((card: any) => {
          const tags = Array.isArray(card.tags) 
            ? card.tags 
            : typeof card.tags === 'string' 
              ? card.tags.split(',').map((t: string) => t.trim()).filter((t: string) => t)
              : [];
          tags.forEach((tag: string) => allTags.add(tag.toLowerCase()));
        });
        
        setAvailableTags(Array.from(allTags).sort());
      } catch (err) {
        console.error('Error fetching tags:', err);
      }
    };

    fetchTags();
  }, [token, providedTags]);

  const handleTagToggle = (tag: string) => {
    if (selectedTags.includes(tag)) {
      onChange(selectedTags.filter(t => t !== tag));
    } else {
      onChange([...selectedTags, tag]);
    }
  };

  const handleAddNewTag = () => {
    const trimmedTag = newTagInput.trim().toLowerCase();
    if (trimmedTag && !selectedTags.includes(trimmedTag)) {
      onChange([...selectedTags, trimmedTag]);
      if (!availableTags.includes(trimmedTag)) {
        setAvailableTags([...availableTags, trimmedTag].sort());
      }
      setNewTagInput('');
      setShowNewTagInput(false);
    }
  };

  const handleRemoveTag = (tag: string) => {
    onChange(selectedTags.filter(t => t !== tag));
  };

  useEffect(() => {
    if (showNewTagInput && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showNewTagInput]);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Tags
      </label>
      
      {/* Selected tags */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {selectedTags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-3 py-1 bg-accent/10 text-accent dark:bg-accent/20 dark:text-accent rounded-full text-sm font-medium"
            >
              {tag}
              <button
                type="button"
                onClick={() => handleRemoveTag(tag)}
                className="ml-1 text-accent dark:text-accent hover:text-accent/80 dark:hover:text-accent/80"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Available tags */}
      <div className="flex flex-wrap gap-2 mb-2">
        {availableTags
          .filter(tag => !selectedTags.includes(tag))
          .map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={() => handleTagToggle(tag)}
              className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
            >
              + {tag}
            </button>
          ))}
        
        {!showNewTagInput && (
          <button
            type="button"
            onClick={() => setShowNewTagInput(true)}
            className="px-3 py-1 border-2 border-dashed border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 rounded-full text-sm hover:border-accent/80 dark:hover:border-accent hover:text-accent dark:hover:text-accent transition-colors duration-200"
          >
            + New Tag
          </button>
        )}
      </div>

      {/* New tag input */}
      {showNewTagInput && (
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={newTagInput}
            onChange={(e) => setNewTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddNewTag();
              } else if (e.key === 'Escape') {
                setShowNewTagInput(false);
                setNewTagInput('');
              }
            }}
            placeholder="Enter new tag name"
            className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-accent focus:border-accent dark:bg-gray-800 dark:text-darktext text-sm"
          />
          <button
            type="button"
            onClick={handleAddNewTag}
            disabled={!newTagInput.trim()}
            className="px-3 py-2 bg-accent text-white rounded-md hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors duration-200"
          >
            Add
          </button>
          <button
            type="button"
            onClick={() => {
              setShowNewTagInput(false);
              setNewTagInput('');
            }}
            className="px-3 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 text-sm transition-colors duration-200"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
};

export default TagSelector;

