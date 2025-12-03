import React from 'react';
import { Link } from 'react-router-dom';
import { MemoryVisualization } from '../components/MemoryVisualization';
import { MemoryRetentionGraph } from '../components/MemoryRetentionGraph';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#fdf2ff] via-white to-[#e5f0ff] text-gray-900">
      {/* Hero Section with simple nav */}
      <section className="relative min-h-screen px-6 py-10 flex flex-col">
        {/* Top nav */}
        <div className="max-w-6xl mx-auto w-full flex items-center justify-between mb-16">
          <div className="flex items-center gap-3">
            <img
              src="/logo-cue.png"
              alt="Cue logo"
              className="h-8 w-auto"
            />
            <span className="font-semibold text-gray-900">Cue</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm">
            <a href="#features" className="text-gray-600 hover:text-gray-900">
              Features
            </a>
            <a href="#how-it-works" className="text-gray-600 hover:text-gray-900">
              How it works
            </a>
            <Link
              to="/login"
              className="px-4 py-2 rounded-full border border-gray-200 text-gray-900 hover:bg-gray-50"
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
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-3xl mx-auto">
            <p className="text-lg md:text-xl text-gray-500 mb-4">
              LLM-powered flashcards that come to you.
            </p>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-semibold tracking-tight mb-6">
              Remember Everything
              <br />
              That Matters
            </h1>
            <p className="text-lg md:text-xl text-gray-500 mb-10">
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
                className="px-8 py-3 bg-white border border-gray-200 text-gray-900 font-medium rounded-full hover:bg-gray-50"
              >
                See How It Works
              </a>
            </div>
            <p className="text-sm text-gray-400">
              No credit card required • 2 minute setup
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4">
              A Smarter Way to Learn
            </h2>
            <p className="text-lg text-gray-500">
              Learning tools that actually fit into your life.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1: Upload & Generate */}
            <div className="rounded-2xl p-8 border border-gray-200 bg-white shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-gray-900 text-white flex items-center justify-center mb-6">
                <span className="text-xl">★</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Upload & Generate</h3>
              <p className="text-gray-600">
                Drop in a PDF—book chapters, papers, notes—and let Cue generate
                flashcards for you instantly.
              </p>
            </div>

            {/* Feature 2: Review Anywhere */}
            <div className="rounded-2xl p-8 border border-gray-200 bg-white shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-gray-900 text-white flex items-center justify-center mb-6">
                <span className="text-xl">💬</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Review Anywhere</h3>
              <p className="text-gray-600">
                Flashcards arrive via text. Review in line, at the gym, between
                meetings—no app required.
              </p>
            </div>

            {/* Feature 3: Track Your Progress */}
            <div className="rounded-2xl p-8 border border-gray-200 bg-white shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-gray-900 text-white flex items-center justify-center mb-6">
                <span className="text-xl">📈</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Track Your Progress</h3>
              <p className="text-gray-600">
                Retention graphs, automatically generated improvement reports,
                and insights into what you're mastering.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Memory retention graph (light) */}
      <MemoryRetentionGraph />

      {/* Product screenshots section */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4">
              See Cue in Action
            </h2>
            <p className="text-lg text-gray-500">
              A quick look at how your cards, reviews, and progress come together.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 mb-10">
            <div className="rounded-3xl overflow-hidden border border-gray-200 bg-gray-50">
              <img
                src="/screenshots/dashboard.png"
                alt="Cue dashboard overview"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="space-y-6">
              <div className="rounded-2xl overflow-hidden border border-gray-200 bg-gray-50">
                <img
                  src="/screenshots/progress_graph.png"
                  alt="Learning progress and retention graphs in Cue"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="rounded-2xl overflow-hidden border border-gray-200 bg-gray-50">
                  <img
                    src="/screenshots/import_features.png"
                    alt="Import features for PDFs and notes"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="rounded-2xl overflow-hidden border border-gray-200 bg-gray-50">
                  <img
                    src="/screenshots/sms.png"
                    alt="SMS-based review flow"
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Network visualization section (dark card on light background) */}
      <div className="bg-white">
        <MemoryVisualization />
      </div>

      {/* Final CTA Section */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-semibold mb-4">
            Ready to Transform How You Learn?
          </h2>
          <p className="text-lg text-gray-500 mb-8">
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

