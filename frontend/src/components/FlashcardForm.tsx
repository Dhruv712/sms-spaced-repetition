import React, { useState } from 'react';
import axios from 'axios';

interface Props {
  onSuccess: () => void;
}

const FlashcardForm: React.FC<Props> = ({ onSuccess }) => {
  const [concept, setConcept] = useState('');
  const [definition, setDefinition] = useState('');
  const [tags, setTags] = useState('');

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

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
      <h2>Add a New Flashcard</h2>
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
      <input
        type="text"
        placeholder="Tags (comma separated)"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
        style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
      />
      <button type="submit">Add Flashcard</button>
    </form>
  );
};

export default FlashcardForm;
