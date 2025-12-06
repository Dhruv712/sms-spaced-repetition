const PHONE_MODAL_SKIP_KEY = 'cue_phone_modal_skip_timestamp';
const SKIP_COOLDOWN_HOURS = 24;

function getStorage(): Storage | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

/**
 * Record that the user clicked "Skip for now" on the phone modal
 */
export function recordPhoneModalSkip(): void {
  const storage = getStorage();
  if (!storage) return;
  
  const timestamp = Date.now();
  storage.setItem(PHONE_MODAL_SKIP_KEY, timestamp.toString());
}

/**
 * Check if the phone modal should be shown
 * Returns false if user clicked "Skip for now" within the last 24 hours
 */
export function shouldShowPhoneModal(): boolean {
  const storage = getStorage();
  if (!storage) return true; // Default to showing if localStorage unavailable
  
  const skipTimestamp = storage.getItem(PHONE_MODAL_SKIP_KEY);
  if (!skipTimestamp) {
    return true; // Never skipped, show modal
  }
  
  const skipTime = parseInt(skipTimestamp, 10);
  if (isNaN(skipTime)) {
    return true; // Invalid timestamp, show modal
  }
  
  const now = Date.now();
  const hoursSinceSkip = (now - skipTime) / (1000 * 60 * 60);
  
  // Show modal if 24 hours have passed since skip
  return hoursSinceSkip >= SKIP_COOLDOWN_HOURS;
}

/**
 * Clear the skip timestamp (useful if user adds phone number)
 */
export function clearPhoneModalSkip(): void {
  const storage = getStorage();
  if (!storage) return;
  storage.removeItem(PHONE_MODAL_SKIP_KEY);
}

