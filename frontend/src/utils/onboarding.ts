export interface OnboardingState {
  step: number;
  completed: boolean;
}

const ONBOARDING_PREFIX = 'cue_onboarding_v1_';

function getStorage(): Storage | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function getOnboardingKey(email?: string | null): string | null {
  if (!email) return null;
  return `${ONBOARDING_PREFIX}${email}`;
}

export function getOnboardingState(email?: string | null): OnboardingState {
  const storage = getStorage();
  const key = getOnboardingKey(email);
  if (!storage || !key) {
    return { step: 0, completed: false };
  }

  const raw = storage.getItem(key);
  if (!raw) {
    return { step: 0, completed: false };
  }

  try {
    const parsed = JSON.parse(raw) as Partial<OnboardingState>;
    return {
      step: typeof parsed.step === 'number' ? parsed.step : 0,
      completed: !!parsed.completed,
    };
  } catch {
    return { step: 0, completed: false };
  }
}

export function setOnboardingState(
  email: string | null | undefined,
  state: OnboardingState
): void {
  const storage = getStorage();
  const key = getOnboardingKey(email ?? undefined);
  if (!storage || !key) return;

  storage.setItem(
    key,
    JSON.stringify({
      step: state.step,
      completed: !!state.completed,
    })
  );
}

export function markOnboardingCompleted(email?: string | null): void {
  setOnboardingState(email, { step: 0, completed: true });
}

export function resetOnboarding(email?: string | null): void {
  const storage = getStorage();
  const key = getOnboardingKey(email);
  if (!storage || !key) return;
  storage.removeItem(key);
}


