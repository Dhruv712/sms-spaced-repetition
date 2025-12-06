# UI/UX Redesign Plan

Based on user feedback, this document outlines the comprehensive redesign plan for Cue's interface.

## Overview
The redesign focuses on:
- **Gamification** of the dashboard
- **Simplified navigation** (merge Flashcards & Decks)
- **Streamlined content creation** (unified "New" button with smart modals)
- **Minimal, dark aesthetic** matching the landing page
- **Reduced clutter** (profile becomes icon, help becomes floating button)

---

## 1. Dashboard Redesign (Gamification Focus)

### Current State
- Too many stats displayed
- Multiple components: ComparisonCards, ReviewStats, DailySummary, AccuracyGraph, WeakestAreas, ConfusionBreakdown, KnowledgeMap
- Stats are neutrally/negatively framed

### Target State
- **Primary focus: Streak visualization** (make it prominent and celebratory)
- **Activity grid** (keep, but make it secondary)
- **Most challenging cards** (keep at bottom)
- **All stats positively framed** (e.g., "You've reviewed X cards!" instead of "X cards reviewed")
- Remove or minimize: ComparisonCards, ReviewStats, DailySummary, AccuracyGraph, WeakestAreas, ConfusionBreakdown, KnowledgeMap

### Implementation Steps
1. **Create new `GamifiedDashboard` component** that:
   - Shows streak prominently at top (large, celebratory design)
   - Displays activity heatmap below streak
   - Shows "Most Challenging Cards" at bottom
   - Uses positive language throughout
   - Adds celebratory animations/emojis for milestones

2. **Update `DashboardPage.tsx`**:
   - Replace current component grid with new gamified layout
   - Remove or conditionally hide less important components
   - Add positive framing to all remaining stats

3. **Backend changes** (if needed):
   - Ensure `/dashboard/stats` returns streak data prominently
   - Add any gamification metrics (badges, achievements, etc.) if desired

---

## 2. Merge Flashcards & Decks Pages

### Current State
- Two separate pages: `/flashcards` and `/decks`
- Flashcards page shows all flashcards with deck filtering
- Decks page shows deck management

### Target State
- **Single "Decks" page** (`/decks`)
- Shows all decks in a grid/list view
- Clicking a deck shows its flashcards inline or in a modal
- Remove `/flashcards` route entirely

### Implementation Steps
1. **Update `DecksPage.tsx`**:
   - Add flashcard viewing functionality (inline or modal)
   - Remove separate flashcards route
   - Integrate flashcard creation into deck context

2. **Update `App.tsx` routing**:
   - Remove `/flashcards` route
   - Update all navigation links to point to `/decks`

3. **Update `Navbar.tsx`**:
   - Remove "Flashcards" link
   - Keep only "Decks" link

4. **Update onboarding flow**:
   - Remove Step 2 (Flashcards) from onboarding
   - Adjust step numbers accordingly

---

## 3. Unified "New" Button with Smart Modals

### Current State
- Flashcard creation via `FlashcardForm` component
- Deck creation via form on Decks page
- PDF/Anki import separate components

### Target State
- **"New" button at top of Decks page**
- Clicking "New" opens modal with two options:
  - "New flashcard(s)"
  - "New deck"
- **"New flashcard(s)" modal**:
  - Text box (can paste lists)
  - Deck selector (multi-select)
  - GPT processes and structures the input
  - Creates multiple flashcards from pasted content
- **"New deck" modal**:
  - Three options: "From scratch", "From PDF", "From Anki deck"
  - "From scratch" → creates deck → immediately opens flashcard modal with deck pre-selected
  - "From PDF" → existing PDF import flow
  - "From Anki deck" → existing Anki import flow

### Implementation Steps
1. **Create `NewContentModal.tsx` component**:
   - First screen: "New flashcard(s)" or "New deck" buttons
   - Handles routing to appropriate sub-modal

2. **Create `NewFlashcardModal.tsx` component**:
   - Large text area for input (supports pasting lists)
   - Multi-select deck dropdown
   - "Process with GPT" button
   - Backend endpoint to parse and structure flashcard data
   - Creates flashcards in selected decks

3. **Create `NewDeckModal.tsx` component**:
   - Three option buttons: "From scratch", "From PDF", "From Anki deck"
   - "From scratch" → creates deck → triggers flashcard modal with deck pre-selected
   - "From PDF" → opens existing `PdfImport` component
   - "From Anki deck" → opens existing `AnkiImport` component

4. **Backend changes**:
   - Create `/flashcards/batch-create` endpoint that:
     - Accepts raw text input
     - Uses GPT to parse and structure into concept/definition pairs
     - Creates multiple flashcards in specified decks
   - Ensure deck creation returns deck ID for pre-selection

5. **Update `DecksPage.tsx`**:
   - Add "New" button at top
   - Integrate new modals
   - Remove old flashcard/deck creation forms

---

## 4. Profile → Profile Picture Icon

### Current State
- Full `/profile` page with form
- Profile link in navbar

### Target State
- **Profile picture icon in top right of navbar** (next to "Get Premium")
- Clicking icon opens profile modal/dropdown
- Remove `/profile` route (or keep for deep linking, but hide from nav)

### Implementation Steps
1. **Create `ProfileDropdown.tsx` or `ProfileModal.tsx`**:
   - Shows user profile picture (or default avatar)
   - Clicking opens dropdown/modal with profile settings
   - Includes all current profile fields (phone, timezone, SMS settings, etc.)

2. **Update `Navbar.tsx`**:
   - Remove "Profile" link from menu
   - Add profile picture icon in top right
   - Position next to "Get Premium" button

3. **Update `ProfilePage.tsx`** (optional):
   - Keep for deep linking if needed
   - Or redirect to dashboard with profile modal open

4. **Update onboarding flow**:
   - Step 4 (Profile) should now open profile modal instead of navigating to page

---

## 5. Help → Floating Question Mark Button

### Current State
- Help link in navbar
- `/help` page

### Target State
- **Floating question mark button in bottom left corner**
- Clicking opens help modal or navigates to help page
- Remove "Help" link from navbar

### Implementation Steps
1. **Create `FloatingHelpButton.tsx` component**:
   - Fixed position bottom left
   - Question mark icon
   - Styled to match dark/red aesthetic
   - Clicking opens help modal or navigates to `/help`

2. **Update `App.tsx` or create layout component**:
   - Add `FloatingHelpButton` to main layout (outside routes)
   - Ensure it appears on all pages except landing/login/register

3. **Update `Navbar.tsx`**:
   - Remove "Help" link from menu

---

## 6. Get Premium Button Styling

### Current State
- "Get Premium" link in navbar (text link)

### Target State
- **Button with different background color** (red/accent color)
- Positioned in top right next to profile picture
- Stands out visually

### Implementation Steps
1. **Update `Navbar.tsx`**:
   - Change "Get Premium" from text link to styled button
   - Use `bg-accent` (red) or similar prominent color
   - Position in top right section with profile icon

---

## 7. Branding & Color Scheme Update

### Current State
- White/dull gray/blue color scheme
- Accent color: `#ff4c3d` (red) defined but not widely used
- Landing page uses dark/red/minimal aesthetic

### Target State
- **Dark, red, minimal aesthetic** matching landing page
- Support light theme but change accent colors
- Use red (`#ff4c3d` or similar) as primary accent
- Dark backgrounds (`#0f0f0f`, `#1a1a1a`) for dark mode
- Minimal, clean design

### Implementation Steps
1. **Update `tailwind.config.js`**:
   - Ensure `accent: '#ff4c3d'` is properly defined
   - Add dark mode color palette matching landing page
   - Update primary/secondary colors to be more minimal

2. **Update component styling**:
   - Replace blue accents with red accents where appropriate
   - Use dark backgrounds in dark mode
   - Ensure light theme still works but with updated accent colors

3. **Update `index.css`**:
   - Ensure dark mode styles match landing page aesthetic
   - Update accent color usage throughout

4. **Review all pages**:
   - Dashboard, Decks, Profile (modal), etc.
   - Ensure consistent dark/red/minimal aesthetic
   - Test both light and dark themes

---

## Implementation Priority

### Phase 1: Core Navigation & Structure (High Priority)
1. Merge Flashcards & Decks pages
2. Update routing and navigation
3. Create unified "New" button and modals

### Phase 2: UI Polish (Medium Priority)
4. Dashboard gamification
5. Profile → icon conversion
6. Help → floating button
7. Get Premium button styling

### Phase 3: Branding (Medium Priority)
8. Color scheme update
9. Dark/red aesthetic implementation
10. Light theme accent color updates

---

## Technical Considerations

### Backend Changes Required
1. **New endpoint**: `/flashcards/batch-create`
   - Accepts: `{ raw_text: string, deck_ids: number[] }`
   - Uses GPT to parse and structure flashcards
   - Returns created flashcard IDs

2. **GPT Integration**:
   - Prompt engineering for flashcard parsing
   - Handle various input formats (lists, notes, etc.)
   - Error handling for malformed input

### Frontend Changes Required
1. **New components**:
   - `GamifiedDashboard.tsx`
   - `NewContentModal.tsx`
   - `NewFlashcardModal.tsx`
   - `NewDeckModal.tsx`
   - `ProfileDropdown.tsx` or `ProfileModal.tsx`
   - `FloatingHelpButton.tsx`

2. **Updated components**:
   - `DashboardPage.tsx`
   - `DecksPage.tsx`
   - `Navbar.tsx`
   - `App.tsx` (routing)

3. **Removed/deprecated**:
   - `FlashcardsPage.tsx` (functionality merged into DecksPage)
   - `/flashcards` route

### Migration Considerations
- Existing bookmarks to `/flashcards` should redirect to `/decks`
- Onboarding flow needs updates
- Any external links to old routes need updating

---

## Testing Checklist

- [ ] Dashboard shows streak prominently
- [ ] Activity grid displays correctly
- [ ] Most challenging cards at bottom
- [ ] All stats use positive framing
- [ ] Decks page shows all decks
- [ ] Clicking deck shows flashcards
- [ ] "New" button opens correct modal
- [ ] "New flashcard(s)" processes lists correctly
- [ ] "New deck" → "From scratch" flow works
- [ ] Profile icon opens profile modal
- [ ] Help button appears bottom left
- [ ] Get Premium button styled correctly
- [ ] Dark mode matches landing page
- [ ] Light mode works with new accents
- [ ] Onboarding flow updated
- [ ] All navigation links updated
- [ ] Mobile responsive design maintained

---

## Notes

- Keep existing functionality intact during redesign
- Test thoroughly before removing old routes
- Consider user migration path for bookmarks/links
- Maintain accessibility throughout
- Ensure mobile experience is polished

