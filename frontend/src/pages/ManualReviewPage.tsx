import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Flashcard {
  id: number;
  concept: string;
  definition: string;
}

const ManualReviewPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [selectedCard, setSelectedCard] = useState<Flashcard | null>(null);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);

  const userId = 1; // hardcoded for now

  useEffect(() => {
    axios
      .get<Flashcard[]>(`http://localhost:8000/flashcards/due/${userId}`)
      .then((res) => setFlashcards(res.data))
      .catch((err) => console.error('Error fetching due flashcards:', err));
  }, []);

  const handleReview = () => {
    if (!selectedCard || !answer.trim()) return;

    axios
      .post('http://localhost:8000/reviews/manual_review', {
        user_id: userId,
        flashcard_id: selectedCard.id,
        answer: answer.trim(),
      })
      .then((res) => {
        setFeedback(res.data.llm_feedback);
        setFlashcards((prev) => prev.filter((c) => c.id !== selectedCard.id));
        setSelectedCard(null);
        setAnswer('');
      })
      .catch((err) => console.error('Review submission failed:', err));
  };

  return (
    <div className="container">
      <h2 className="text-2xl font-bold mb-4">Manual Review</h2>

      {!selectedCard ? (
        <ul>
          {flashcards.map((card) => (
            <li key={card.id} className="card">
              <strong>{card.concept}</strong>
              <button
                className="btn ml-4"
                onClick={() => {
                  setSelectedCard(card);
                  setFeedback(null);
                }}
              >
                Review
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <div className="card">
          <div className="mb-2"><strong>Concept:</strong> {selectedCard.concept}</div>
          <textarea
            className="w-full p-2 border rounded mb-2"
            placeholder="Your answer..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
          />
          <div className="flex gap-2">
            <button className="btn" onClick={handleReview}>
              Submit Answer
            </button>
            <button className="btn-secondary" onClick={() => setSelectedCard(null)}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {feedback && (
        <div className="mt-4 p-3 border-t">
          <strong>LLM Feedback:</strong>
          <p>{feedback}</p>
        </div>
      )}
    </div>
  );
};

export default ManualReviewPage;
