# Feature Implementation Plan

## Overview
This document outlines the implementation plan for 5 new features to enhance the spaced repetition app.

---

## Feature 1: Show Deck Name in SMS and Manual Review

### Goal
Display which deck a flashcard belongs to when reviewing via SMS or manual review.

### Implementation Steps

#### Backend:
1. **Update `loop_message_service.py`**:
   - Modify `send_flashcard()` to include deck name in message
   - Format: `"[Deck: Biology] What is DNA?"` or similar
   - Handle cards without decks gracefully

#### Frontend:
2. **Update `ManualReviewPage.tsx`**:
   - Fetch deck information when loading flashcards
   - Display deck name above/below the flashcard concept
   - Style: Small badge or text indicator

3. **Update `DeckReviewPage.tsx`**:
   - Already shows deck context, but verify it's clear

### Files to Modify:
- `app/services/loop_message_service.py`
- `frontend/src/pages/ManualReviewPage.tsx`
- `app/routes/flashcards.py` (ensure deck info is returned in due cards endpoint)

### Estimated Complexity: Low
### Estimated Time: 30-45 minutes

---

## Feature 2: Per-Card Difficulty Curve (Top 5 Most Difficult Cards)

### Goal
Show the top 5 most difficult cards based on user's accuracy, with their average accuracy and correct answer.

### Implementation Steps

#### Backend:
1. **Create new endpoint `/dashboard/difficult-cards`**:
   - Calculate accuracy per flashcard: `correct_reviews / total_reviews`
   - Filter cards with at least 3 reviews (to avoid noise)
   - Sort by lowest accuracy
   - Return top 5 with: flashcard_id, concept, definition, accuracy, total_reviews, correct_reviews

#### Frontend:
2. **Create `DifficultCards.tsx` component**:
   - Display cards in a clean list/card format
   - Show: concept, accuracy percentage, total reviews, definition (collapsible?)
   - Add to Dashboard page

### Files to Create/Modify:
- `app/routes/dashboard.py` (add endpoint)
- `frontend/src/components/DifficultCards.tsx` (new)
- `frontend/src/pages/DashboardPage.tsx` (add component)

### Estimated Complexity: Low-Medium
### Estimated Time: 1-2 hours

---

## Feature 3: Knowledge Map/Cloud (3D Embedding Visualization)

### Goal
Create a 3D visualization where similar concepts are closer together using embeddings.

### Implementation Steps

#### Backend:
1. **Option A: Use OpenAI Embeddings** (More accurate, requires API calls):
   - Create endpoint `/dashboard/knowledge-map`
   - For each flashcard, generate embedding using OpenAI API
   - Store embeddings (optional: cache in database)
   - Use PCA/t-SNE to reduce to 3D coordinates
   - Return: flashcard_id, concept, x, y, z coordinates

2. **Option B: Tag-based Clustering** (Simpler, no API calls):
   - Group cards by tags
   - Use tag similarity to position cards
   - Less accurate but faster and free

#### Frontend:
3. **Create `KnowledgeMap.tsx` component**:
   - Use Three.js or react-three-fiber for 3D visualization
   - Display cards as points in 3D space
   - Allow rotation, zoom, pan
   - Click on points to see card details
   - Color-code by deck or difficulty

### Files to Create/Modify:
- `app/routes/dashboard.py` (add endpoint)
- `frontend/src/components/KnowledgeMap.tsx` (new)
- `frontend/src/pages/DashboardPage.tsx` (add component)
- `requirements.txt` (add three.js dependencies if needed)

### Estimated Complexity: High
### Estimated Time: 4-6 hours

### Recommendation: Start with Option B (tag-based) for MVP, upgrade to embeddings later

---

## Feature 4: Confusion Breakdown (Most Common Incorrect Answers)

### Goal
Track and display which incorrect answers users type most often for each flashcard.

### Implementation Steps

#### Backend:
1. **Database Schema** (if needed):
   - `CardReview` already has `user_response` and `was_correct`
   - May need to add index on `flashcard_id` and `was_correct` for performance

2. **Create endpoint `/dashboard/confusion-breakdown`**:
   - Query reviews where `was_correct = False`
   - Group by `flashcard_id` and `user_response` (normalize case/spacing)
   - Count occurrences of each wrong answer per flashcard
   - Return: flashcard_id, concept, incorrect_answers array (answer, count)

#### Frontend:
3. **Create `ConfusionBreakdown.tsx` component**:
   - Display cards with their most common wrong answers
   - Show: concept, top 3-5 incorrect answers with counts
   - Visualize with bar chart or list
   - Add to Dashboard

### Files to Create/Modify:
- `app/routes/dashboard.py` (add endpoint)
- `frontend/src/components/ConfusionBreakdown.tsx` (new)
- `frontend/src/pages/DashboardPage.tsx` (add component)

### Estimated Complexity: Medium
### Estimated Time: 2-3 hours

---

## Feature 5: Streak Engagement Reminders

### Goal
Send gentle reminder texts when users are at risk of losing their streak.

### Implementation Steps

#### Backend:
1. **Create `streak_reminder_service.py`**:
   - Function to check if user is at risk (hasn't reviewed today, streak > 0)
   - Check if cards are due and SMS-enabled
   - Determine reminder message based on situation:
     - Cards available: "Don't forget to review today to keep your X-day streak!"
     - No SMS-enabled cards due: "Log onto the web app and go to 'Review Due Cards' to continue your streak"

2. **Update `scheduler_service.py`**:
   - Add function `check_and_send_streak_reminders()`
   - Run this check (maybe once per day, e.g., 6 PM user time)
   - Only send if user hasn't reviewed today and has active streak

3. **Update cron schedule**:
   - Add reminder check to hourly cron or separate daily check

#### Frontend:
4. **No frontend changes needed** (SMS-only feature)

### Files to Create/Modify:
- `app/services/streak_reminder_service.py` (new)
- `app/services/scheduler_service.py` (add reminder logic)
- `app/routes/admin.py` (add cron endpoint for reminders)
- `send_flashcards.py` (add reminder check)

### Estimated Complexity: Medium
### Estimated Time: 2-3 hours

### Considerations:
- Frequency: Once per day max
- Timing: Late afternoon/evening (6-8 PM user time)
- Don't spam: Only if streak > 0 and no review today

---

## Implementation Order Recommendation

1. **Feature 1** (Deck name) - Quick win, low complexity
2. **Feature 2** (Difficult cards) - Useful analytics, straightforward
3. **Feature 4** (Confusion breakdown) - Valuable insights, medium complexity
4. **Feature 5** (Streak reminders) - Engagement feature, medium complexity
5. **Feature 3** (Knowledge map) - Most complex, save for last

---

## Notes

- All features should respect premium/free limits where applicable
- Consider caching for expensive operations (embeddings, aggregations)
- Add proper error handling and logging
- Test with real user data where possible
- Consider mobile responsiveness for all frontend components

