import React, { useState, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { useAuth } from '../contexts/AuthContext';

interface Props {
  onSuccess: () => void;
}

const FlashcardForm: React.FC<Props> = ({ onSuccess }) => {
  const [concept, setConcept] = useState('');
  const [definition, setDefinition] = useState('');
  const [tags, setTags] = useState('');
  const [nlInput, setNlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const formEndRef = useRef<HTMLDivElement | null>(null);
  const { token } = useAuth();

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting || !token) return;
  
    setSubmitting(true);
    setError('');
    try {
      await axios.post('http://localhost:8000/flashcards/', {
        concept,
        definition,
        tags,
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setConcept('');
      setDefinition('');
      setTags('');
      onSuccess();
    } catch (err) {
      console.error('Error creating flashcard:', err);
      setError('Failed to create flashcard. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNaturalSubmit = async () => {
    if (!token) return;
    
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(
        'http://localhost:8000/natural_flashcards/generate_flashcard',
        {
          text: nlInput,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const { concept, definition, tags } = res.data;
      setConcept(concept);
      setDefinition(definition);
      setTags(tags || '');
      scrollToBottom();
    } catch (err) {
      console.error('Error generating flashcard:', err);
      setError('Failed to generate flashcard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      formEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Add a New Flashcard</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="mb-6">
        <textarea
          placeholder="Type something like: 'Make a card about how Pretoria is Elon Musk's birthplace'"
          value={nlInput}
          onChange={(e) => setNlInput(e.target.value)}
          rows={3}
          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <button
          type="button"
          onClick={handleNaturalSubmit}
          disabled={loading || !token}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate from Natural Language'}
        </button>
      </div>

      <form onSubmit={handleManualSubmit} className="space-y-4">
        <div>
          <input
            type="text"
            placeholder="Concept"
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            required
            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <textarea
            placeholder="Definition"
            value={definition}
            onChange={(e) => setDefinition(e.target.value)}
            required
            rows={4}
            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          {definition && (
            <div className="mt-2 p-2 bg-gray-50 rounded">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {definition}
              </ReactMarkdown>
            </div>
          )}
        </div>
        <div>
          <input
            type="text"
            placeholder="Tags (comma separated)"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <button
          type="submit"
          disabled={submitting || !token}
          className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          {submitting ? 'Saving...' : 'Save Flashcard'}
        </button>
      </form>
      <div ref={formEndRef} />
    </div>
  );
};

export default FlashcardForm;
