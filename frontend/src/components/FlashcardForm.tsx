import React, { useState } from 'react';
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
  const [naturalText, setNaturalText] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/flashcards/', {
        user_id: 1, // 🔥 TEMP: hardcoded until we add auth
        concept,
        definition,
        tags,
      });
      setConcept('');
      setDefinition('');
      setTags('');
      onSuccess(); // refresh list
    } catch (err) {
      console.error('Error creating flashcard:', err);
    }
  };

  const handleNaturalSubmit = async () => {
    if (!naturalText.trim()) return;
    setLoading(true);
    setStatusMessage('');
    try {
      const res = await axios.post('http://localhost:8000/natural_flashcards/generate_flashcard', {
        user_id: 1,
        text: naturalText,
      });
      setNaturalText('');
      setStatusMessage(`✅ Created card: ${res.data.concept}`);
      onSuccess();
    } catch (err) {
      console.error('Error generating flashcard:', err);
      setStatusMessage('❌ Failed to generate flashcard.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ marginBottom: '2rem' }}>
      <h2 className="text-lg font-semibold mb-2">Natural Language Flashcard</h2>
      <input
        type="text"
        placeholder='e.g. "Make a card about how mitochondria are the powerhouse of the cell"'
        value={naturalText}
        onChange={(e) => setNaturalText(e.target.value)}
        style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
      />
      <button type="button" onClick={handleNaturalSubmit} className="btn mb-4">
        {loading ? 'Generating...' : 'Generate from Text'}
      </button>
      {statusMessage && <p className="text-sm">{statusMessage}</p>}

      <hr className="my-4" />

      <form onSubmit={handleSubmit}>
        <h2 className="text-lg font-semibold mb-2">Add a Flashcard Manually</h2>
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
        <button type="submit" className="btn mt-2">Add Flashcard</button>
      </form>
    </div>
  );
};

export default FlashcardForm;
