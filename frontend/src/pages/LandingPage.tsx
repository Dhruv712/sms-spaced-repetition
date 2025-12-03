import React from 'react';
import { Link } from 'react-router-dom';
import { MemoryVisualization } from '../components/MemoryVisualization';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 py-20 overflow-hidden">
        {/* Background gradient glow */}
        <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 via-transparent to-blue-500/10 pointer-events-none" />
        
        {/* Brain Icon */}
        <div className="relative z-10 mb-8">
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center shadow-2xl shadow-red-500/50">
            <svg 
              className="w-12 h-12 text-white" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" 
              />
            </svg>
          </div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 text-center max-w-4xl mx-auto">
          <p className="text-xl md:text-2xl text-gray-300 mb-6">
            Tired of forgetting things? Want to remember what you learn?
          </p>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-8 leading-tight">
            Remember Everything<br />
            That Matters
          </h1>
          
          <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            LLM-powered flashcards that come to you. Cue uses spaced repetition and intelligent SMS reminders to make learning stick—automatically.
          </p>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-6">
            <Link
              to="/register"
              className="group px-8 py-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-all duration-200 flex items-center gap-2 shadow-lg shadow-red-500/30 hover:shadow-red-500/50"
            >
              Start Learning Free
              <svg 
                className="w-5 h-5 transition-transform group-hover:translate-x-1" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            
            <Link
              to="/login"
              className="px-8 py-4 bg-transparent border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-black transition-all duration-200"
            >
              See How It Works
            </Link>
          </div>
          
          <p className="text-sm text-gray-500">
            No credit card required • 2 minute setup
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 px-6 bg-black">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              A Smarter Way to Learn
            </h2>
            <p className="text-xl text-gray-400">
              Learning tools that actually fit into your life.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1: Upload & Generate */}
            <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 hover:border-gray-700 transition-colors">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-purple-700 rounded-xl flex items-center justify-center mb-6">
                <svg 
                  className="w-8 h-8 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M13 10V3L4 14h7v7l9-11h-7z" 
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Upload & Generate</h3>
              <p className="text-gray-400 text-lg">
                Drop in a PDF—book chapters, papers, notes—and let Cue generate flashcards for you instantly.
              </p>
            </div>
            
            {/* Feature 2: Review Anywhere */}
            <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 hover:border-gray-700 transition-colors">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center mb-6">
                <svg 
                  className="w-8 h-8 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" 
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Review Anywhere</h3>
              <p className="text-gray-400 text-lg">
                Flashcards arrive via text. Review in line, at the gym, between meetings—no app required.
              </p>
            </div>
            
            {/* Feature 3: Track Your Progress */}
            <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 hover:border-gray-700 transition-colors">
              <div className="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center mb-6">
                <svg 
                  className="w-8 h-8 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" 
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Track Your Progress</h3>
              <p className="text-gray-400 text-lg">
                Retention graphs, automatically generated improvement reports, and insights into what you're mastering.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Brain Optimization Section */}
      <MemoryVisualization />

      {/* Final CTA Section */}
      <section className="py-32 px-6 bg-black">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Remember?
          </h2>
          <p className="text-xl text-gray-400 mb-10">
            Join thousands of learners who are making knowledge stick with Cue.
          </p>
          <Link
            to="/register"
            className="inline-block px-8 py-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-all duration-200 shadow-lg shadow-red-500/30 hover:shadow-red-500/50"
          >
            Get Started Free
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;

