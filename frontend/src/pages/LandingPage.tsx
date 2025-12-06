import React from 'react';
import { Link } from 'react-router-dom';
import { MemoryRetentionGraph } from '../components/MemoryRetentionGraph';
import { NeuralBackground } from '../components/NeuralBackground';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero Section with nav */}
      <section className="relative min-h-screen px-6 py-10 flex flex-col overflow-hidden">
        <NeuralBackground />
        {/* Top nav */}
        <div className="max-w-6xl mx-auto w-full flex items-center justify-between mb-16 relative z-10">
          <div className="flex items-center gap-3">
            <img
              src="/logo-cue.png"
              alt="Cue logo"
              className="h-10 md:h-12 w-auto"
            />
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm">
            <Link
              to="/login"
              className="text-gray-300 hover:text-white"
            >
              Log in
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 rounded-full bg-accent text-white hover:brightness-95"
            >
              Get Started
            </Link>
          </div>
        </div>

        {/* Hero content */}
        <div className="flex-1 flex items-center justify-center relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-semibold tracking-tight mb-6 text-white">
              Remember Everything
              <br />
              That Matters
            </h1>
            <p className="text-lg md:text-xl text-gray-400 mb-10">
              Turn your notes into flashcards with a click. Review them on the go from iMessage.
              Get instant feedback and track your improvement over time.
              Learn smarter.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-4">
              <Link
                to="/register"
                className="group px-8 py-3 bg-accent hover:brightness-95 text-white font-medium rounded-full transition-all duration-200 flex items-center gap-2"
              >
                Get Started Free
                <svg
                  className="w-4 h-4 transition-transform group-hover:translate-x-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </Link>
            </div>
            <p className="text-sm text-gray-500">
              No credit card required • 2 minute setup
            </p>
          </div>
        </div>
      </section>

      {/* Section 1: Texting/SMS - First thing they see */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="rounded-3xl overflow-hidden border border-gray-800 bg-black max-w-xs mx-auto md:max-w-none">
              <img
                src="/screenshots/sms.png"
                alt="SMS-based review flow"
                className="w-full h-auto object-contain"
              />
            </div>
            <div className="space-y-4">
              <h2 className="text-3xl md:text-4xl font-semibold text-white">
                Review from wherever you are
              </h2>
              <p className="text-gray-400 text-lg">
                Flashcards arrive right in your text messages. Reply with your
                answer, and an LLM will grade you and schedule your next review.
                No app required, just iMessage.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: AI can create your flashcards */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="space-y-4">
              <h2 className="text-3xl md:text-4xl font-semibold text-white">
                AI creates your flashcards for you
              </h2>
              <p className="text-gray-400 text-lg">
                Upload PDFs or long-form notes and let an LLM generate
                high-quality flashcards automatically. This is optional - you can
                still create, edit, and organize cards manually whenever you
                want.
              </p>
              <p className="text-gray-500 text-sm">
                You can import PDFs and Anki decks too
              </p>
            </div>
            <div className="rounded-3xl overflow-hidden border border-gray-800 bg-black">
              <img
                src="/screenshots/import_features.png"
                alt="Import PDFs and generate flashcards"
                className="w-full h-auto object-contain"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Graph of accuracy over time */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="rounded-3xl overflow-hidden border border-gray-800 bg-black">
              <img
                src="/screenshots/progress_graph.png"
                alt="Progress and accuracy graphs"
                className="w-full h-auto object-contain"
              />
            </div>
            <div className="space-y-4">
              <h2 className="text-3xl md:text-4xl font-semibold text-white">
                Track your accuracy over time
              </h2>
              <p className="text-gray-400 text-lg">
                See how your accuracy and review volume change over time. Cue
                turns your daily reviews into trends and insights you can act
                on.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Your Brain, Optimized - Memory Retention Graph */}
      <MemoryRetentionGraph />

      {/* Section 4: Spaced repetition */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="space-y-4">
              <h2 className="text-3xl md:text-4xl font-semibold text-white">
                Spaced repetition that actually works
              </h2>
              <p className="text-gray-400 text-lg">
                Cue uses the proven SM-2 algorithm to schedule your reviews at
                the optimal time. Cards you know well appear less frequently,
                while challenging cards come up more often until you master them.
              </p>
            </div>
            <div className="rounded-3xl overflow-hidden border border-gray-800 bg-black">
              <img
                src="/screenshots/dashboard.png"
                alt="Spaced repetition scheduling"
                className="w-full h-auto object-contain"
              />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;

