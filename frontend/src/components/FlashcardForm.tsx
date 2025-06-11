import React, { useState, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface Props {
  onSuccess: () => void;
}

const FlashcardForm: React.FC<Props> = ({ onSuccess }) => {
  const [concept, setConcept] = useState('');
  const [definition, setDefinition] = useState('');
  const [tags, setTags] = useState('');
  const [nlInput, setNlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const formEndRef = useRef<HTMLDivElement | null>(null);

  const [submitting, setSubmitting] = useState(false);

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
  
    setSubmitting(true);
    try {
      await axios.post('http://localhost:8000/flashcards/', {
        user_id: 1,
        concept,
        definition,
        tags,
      });
      setConcept('');
      setDefinition('');
      setTags('');
      onSuccess();
    } catch (err) {
      console.error('Error creating flashcard:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNaturalSubmit = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/natural_flashcards/generate_flashcard', {
        user_id: 1,
        text: nlInput,
      });

      const { concept, definition, tags } = res.data;
      setConcept(concept);
      setDefinition(definition);
      setTags(tags || '');
    //   onSuccess();
    //   scrollToBottom();
    } catch (err) {
      console.error('Error generating flashcard:', err);
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
    <div style={{ marginBottom: '2rem' }}>
      <h2 className="text-lg font-semibold mb-2">Add a New Flashcard</h2>

      <textarea
        placeholder="Type something like: 'Make a card about how Pretoria is Elon Musk's birthplace'"
        value={nlInput}
        onChange={(e) => setNlInput(e.target.value)}
        rows={3}
        style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
      />
      <button
        type="button"
        className="btn mb-4"
        onClick={handleNaturalSubmit}
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate from Natural Language'}
      </button>

      <form onSubmit={handleManualSubmit} className="card">
        <input
          type="text"
          placeholder="Concept"
          value={concept}
          onChange={(e) => setConcept(e.target.value)}
          required
          style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
        />
        <textarea
          placeholder="Definition"
          value={definition}
          onChange={(e) => setDefinition(e.target.value)}
          required
          rows={4}
          style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
        />
        <ReactMarkdown
          children={definition}
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
        />
        <input
          type="text"
          placeholder="Tags (comma separated)"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
        />
        <button type="submit" className="btn mt-2" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save Flashcard'}
        </button>
      </form>
      <div ref={formEndRef} />
    </div>
  );
};

export default FlashcardForm;
