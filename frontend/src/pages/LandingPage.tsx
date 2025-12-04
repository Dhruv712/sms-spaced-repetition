import React from 'react';
import { Link } from 'react-router-dom';
import { MemoryRetentionGraph } from '../components/MemoryRetentionGraph';
import { NeuralBackground } from '../components/NeuralBackground';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero Section with simple nav */}
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
            <a href="#features" className="text-gray-300 hover:text-white">
              Features
            </a>
            <a href="#how-it-works" className="text-gray-300 hover:text-white">
              How it works
            </a>
            <Link
              to="/login"
              className="px-4 py-2 rounded-full border border-gray-700 text-gray-100 hover:bg-gray-900"
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
            <p className="text-lg md:text-xl text-gray-400 mb-4">
              LLM-powered flashcards that come to you.
            </p>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-semibold tracking-tight mb-6 text-white">
              Remember Everything
              <br />
              That Matters
            </h1>
            <p className="text-lg md:text-xl text-gray-400 mb-10">
              Cue uses spaced repetition and intelligent SMS reminders to make
              learning stick—automatically.
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

              <a
                href="#how-it-works"
                className="px-8 py-3 bg-transparent border border-gray-700 text-gray-100 font-medium rounded-full hover:bg-gray-900"
              >
                See How It Works
              </a>
            </div>
            <p className="text-sm text-gray-500">
              No credit card required • 2 minute setup
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-black">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4 text-white">
              A Smarter Way to Learn
            </h2>
            <p className="text-lg text-gray-400">
              Learning tools that actually fit into your life.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1: Upload & Generate */}
            <div className="rounded-2xl p-8 border border-gray-800 bg-[#020617] shadow-[0_18px_45px_rgba(0,0,0,0.6)]">
              <div className="w-12 h-12 rounded-xl bg-accent text-white flex items-center justify-center mb-6">
                <span className="text-xl">★</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Upload & Generate</h3>
              <p className="text-gray-300">
                Drop in a PDF—book chapters, papers, notes—and let Cue generate
                flashcards for you instantly.
              </p>
            </div>

            {/* Feature 2: Review Anywhere */}
            <div className="rounded-2xl p-8 border border-gray-800 bg-[#020617] shadow-[0_18px_45px_rgba(0,0,0,0.6)]">
              <div className="w-12 h-12 rounded-xl bg-accent text-white flex items-center justify-center mb-6">
                <span className="text-xl">💬</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Review Anywhere</h3>
              <p className="text-gray-300">
                Flashcards arrive via text. Review in line, at the gym, between
                meetings—no app required.
              </p>
            </div>

            {/* Feature 3: Track Your Progress */}
            <div className="rounded-2xl p-8 border border-gray-800 bg-[#020617] shadow-[0_18px_45px_rgba(0,0,0,0.6)]">
              <div className="w-12 h-12 rounded-xl bg-accent text-white flex items-center justify-center mb-6">
                <span className="text-xl">📈</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Track Your Progress</h3>
              <p className="text-gray-300">
                Retention graphs, automatically generated improvement reports,
                and insights into what you're mastering.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Memory retention graph + neural visualization */}
      <MemoryRetentionGraph />

      {/* Product screenshots section - individual feature highlights */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-6xl mx-auto space-y-20">
          <div className="text-center">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4 text-white">
              See Cue in Action
            </h2>
            <p className="text-lg text-gray-400">
              A closer look at how Cue helps you remember what matters.
            </p>
          </div>

          {/* 1) Import & generate – text left, image right */}
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                Turn your notes or documents into flashcards in seconds
              </h3>
              <p className="text-gray-400 text-lg">
                Upload PDFs or long-form notes and let an LLM generate
                high-quality flashcards automatically. This is optional—you can
                still create, edit, and organize cards manually whenever you
                want.
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

          {/* 2) SMS – image left, text right */}
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="rounded-3xl overflow-hidden border border-gray-800 bg-black max-w-xs mx-auto">
              <img
                src="/screenshots/sms.png"
                alt="SMS-based review flow"
                className="w-full h-auto object-contain"
              />
            </div>
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                Review from wherever you are
              </h3>
              <p className="text-gray-400 text-lg">
                Reviews show up right in your text messages. Reply with your
                answer, let the LLM grade you, and get your next review
                scheduled—no apps, no friction.
              </p>
            </div>
          </div>

          {/* 3) Track real improvement – text left, image right */}
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                Track real improvement
              </h3>
              <p className="text-gray-400 text-lg">
                See how your accuracy and review volume change over time. Cue
                turns your daily reviews into trends and insights you can act
                on.
              </p>
            </div>
            <div className="rounded-3xl overflow-hidden border border-gray-800 bg-black">
              <img
                src="/screenshots/progress_graph.png"
                alt="Progress and accuracy graphs"
                className="w-full h-auto object-contain"
              />
            </div>
          </div>

          {/* 4) See your learning at a glance – image left, text right */}
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div className="rounded-3xl overflow-hidden border border-gray-800 bg-black">
              <img
                src="/screenshots/dashboard.png"
                alt="Cue dashboard overview"
                className="w-full h-auto object-contain"
              />
            </div>
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                See your learning at a glance
              </h3>
              <p className="text-gray-400 text-lg">
                The dashboard gives you a big-picture view of your streaks,
                review activity, and accuracy so you always know how your
                learning is trending.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-semibold mb-4 text-white">
            Ready to Transform How You Learn?
          </h2>
          <p className="text-lg text-gray-400 mb-8">
            Start building knowledge that lasts.
          </p>
          <Link
            to="/register"
            className="inline-block px-8 py-3 bg-accent hover:brightness-95 text-white font-medium rounded-full transition-all duration-200"
          >
            Get Started Free
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;

