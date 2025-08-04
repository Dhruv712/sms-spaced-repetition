import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
  tags: string[];
  source_url?: string;
}

const DeckReviewPage: React.FC = () => {
  const { deck_id } = useParams<{ deck_id: string }>();
  const { token } = useAuth();
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [current, setCurrent] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [grading, setGrading] = useState(false);
  const [grade, setGrade] = useState<any>(null);
  const [finished, setFinished] = useState(false);
  const [flipped, setFlipped] = useState(false);

  useEffect(() => {
    if (!token || !deck_id) return;
    axios.get(`http://localhost:8000/flashcards/decks/${deck_id}/all-flashcards`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(res => setFlashcards(res.data));
  }, [token, deck_id]);

  const handleGrade = async () => {
    setGrading(true);
    setGrade(null);
    try {
      const res = await axios.post('http://localhost:8000/reviews/manual_review', {
        flashcard_id: flashcards[current].id,
        answer: userAnswer,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGrade(res.data);
    } catch (e) {
      setGrade({ error: 'Grading failed.' });
    }
    setGrading(false);
  };

  const handleNext = () => {
    setUserAnswer('');
    setGrade(null);
    setFlipped(false);
    if (current + 1 < flashcards.length) {
      setCurrent(current + 1);
    } else {
      setFinished(true);
    }
  };

  const handleFlip = () => {
    setFlipped(true);
  };

  if (!token) return <div>Please log in.</div>;
  if (flashcards.length === 0) return <div>No flashcards in this deck.</div>;
  if (finished) return <div>Review complete!</div>;

  const card = flashcards[current];

  return (
    <div className="max-w-xl mx-auto p-6 bg-white dark:bg-gray-900 rounded shadow">
      <h2 className="text-xl font-bold mb-4">Review Deck</h2>
      <div className="mb-2 text-sm text-gray-500 dark:text-gray-300">Card {current + 1} of {flashcards.length}</div>
      <div className="mb-4">
        <div className="font-semibold">Concept:</div>
        <div>{card.concept}</div>
      </div>
      {!flipped && !grade && (
        <>
          <div className="mb-4">
            <div className="font-semibold">Your Answer:</div>
            <textarea
              className="w-full border rounded p-2"
              rows={3}
              value={userAnswer}
              onChange={e => setUserAnswer(e.target.value)}
              disabled={grading || !!grade}
            />
          </div>
          <button
            className="bg-primary-500 text-white px-4 py-2 rounded mr-2"
            onClick={handleGrade}
            disabled={grading || !!grade}
          >
            {grading ? 'Grading...' : 'Submit Answer'}
          </button>
          <button
            className="bg-secondary-500 text-white px-4 py-2 rounded"
            onClick={handleFlip}
            disabled={grading || !!grade}
          >
            Flip Card
          </button>
        </>
      )}
      {flipped && !grade && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900 rounded">
          <div className="font-semibold mb-2">Definition:</div>
          <div className="mb-4">{card.definition}</div>
          <button className="bg-secondary-500 text-white px-4 py-2 rounded" onClick={handleNext}>
            {current + 1 < flashcards.length ? 'Next Card' : 'Finish Review'}
          </button>
        </div>
      )}
      {grade && (
        <div className="mt-4 p-3 bg-gray-100 rounded">
          {grade.error ? (
            <div className="text-red-600">{grade.error}</div>
          ) : (
            <>
              <div><strong>Correct:</strong> {grade.was_correct !== undefined ? (grade.was_correct ? 'Yes' : 'No') : (grade.correct ? 'Yes' : 'No')}</div>
              <div><strong>LLM Feedback:</strong> {grade.llm_feedback || grade.feedback || 'No feedback returned.'}</div>
            </>
          )}
          <button className="mt-2 bg-secondary-500 text-white px-4 py-2 rounded" onClick={handleNext}>
            {current + 1 < flashcards.length ? 'Next Card' : 'Finish Review'}
          </button>
        </div>
      )}
    </div>
  );
};

export default DeckReviewPage; 