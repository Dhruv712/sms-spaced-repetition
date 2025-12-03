import React from "react";
import { MemoryVisualization } from "./MemoryVisualization";
import {
  CartesianGrid,
  ResponsiveContainer,
  Area,
  AreaChart,
  XAxis,
  YAxis,
} from "recharts";

const data = [
  { day: 0, withoutSR: 100, withSR: 100 },
  { day: 1, withoutSR: 70, withSR: 100 },
  { day: 2, withoutSR: 50, withSR: 95 },
  { day: 3, withoutSR: 35, withSR: 100 },
  { day: 5, withoutSR: 25, withSR: 95 },
  { day: 7, withoutSR: 20, withSR: 100 },
  { day: 10, withoutSR: 15, withSR: 95 },
  { day: 14, withoutSR: 10, withSR: 100 },
  { day: 21, withoutSR: 8, withSR: 98 },
  { day: 30, withoutSR: 5, withSR: 98 },
];

export const MemoryRetentionGraph: React.FC = () => {
  return (
    <section id="how-it-works" className="py-32 px-6 bg-black">
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          {/* Content */}
          <div>
            <h2 className="mb-6 text-white text-5xl leading-tight">
              Your Brain,
              <br />
              Optimized
            </h2>
            <p className="text-gray-300 text-lg mb-6 leading-relaxed">
              Here's the thing: you forget most of what you learn. Not because
              you're bad at learning, but because your brain naturally clears
              out information you don't use.
            </p>
            <p className="text-gray-300 text-lg mb-6 leading-relaxed">
              Spaced repetition works with this reality. It shows you
              information right before you'd forget it—so your brain says
              &quot;okay, this must be important&quot; and holds onto it
              longer.
            </p>
            <p className="text-gray-300 text-lg leading-relaxed">
              Do this enough times, and what used to slip away becomes
              permanent.
            </p>
          </div>

          {/* Visualization */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-red-50 to-blue-50 rounded-3xl p-8 border border-gray-200 shadow-lg">
              <div className="mb-6">
                <h3 className="text-gray-900 text-xl mb-2">
                  Memory Retention Over Time
                </h3>
                <div className="flex flex-wrap gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-gray-400" />
                    <span className="text-gray-600">
                      Without Spaced Repetition
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <span className="text-gray-600">
                      With Spaced Repetition
                    </span>
                  </div>
                </div>
              </div>

              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="colorWithSR" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="5%"
                        stopColor="rgb(239, 68, 68)"
                        stopOpacity={0.3}
                      />
                      <stop
                        offset="95%"
                        stopColor="rgb(239, 68, 68)"
                        stopOpacity={0}
                      />
                    </linearGradient>
                    <linearGradient
                      id="colorWithoutSR"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="5%"
                        stopColor="rgb(156, 163, 175)"
                        stopOpacity={0.3}
                      />
                      <stop
                        offset="95%"
                        stopColor="rgb(156, 163, 175)"
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="day"
                    stroke="#9ca3af"
                    tick={{ fill: "#6b7280" }}
                    label={{
                      value: "Days",
                      position: "insideBottom",
                      offset: -5,
                      fill: "#6b7280",
                    }}
                  />
                  <YAxis
                    stroke="#9ca3af"
                    tick={{ fill: "#6b7280" }}
                    label={{
                      value: "Retention %",
                      angle: -90,
                      position: "insideLeft",
                      fill: "#6b7280",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="withoutSR"
                    stroke="rgb(156, 163, 175)"
                    strokeWidth={2}
                    fill="url(#colorWithoutSR)"
                  />
                  <Area
                    type="monotone"
                    dataKey="withSR"
                    stroke="rgb(239, 68, 68)"
                    strokeWidth={3}
                    fill="url(#colorWithSR)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};


