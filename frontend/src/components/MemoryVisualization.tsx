import { useEffect, useState } from "react";

export function MemoryVisualization() {
  const [activeNodes, setActiveNodes] = useState<number[]>([]);
  
  // Simulate neural connections lighting up
  useEffect(() => {
    const interval = setInterval(() => {
      const randomNodes = Array.from(
        { length: 5 }, 
        () => Math.floor(Math.random() * 12)
      );
      setActiveNodes(randomNodes);
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Create a grid of connection points
  const nodes = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    x: (i % 4) * 33.33,
    y: Math.floor(i / 4) * 50,
  }));
  
  return (
    <section className="py-32 px-6 relative overflow-hidden">
      <div className="max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Visual */}
          <div className="relative h-96 rounded-2xl bg-gradient-to-br from-gray-900 to-black border border-gray-800 p-12 overflow-hidden">
            {/* Connection lines */}
            <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.3 }}>
              {nodes.map((node, i) => 
                nodes.slice(i + 1).map((target, j) => {
                  const isActive = activeNodes.includes(node.id) && activeNodes.includes(target.id);
                  return (
                    <line
                      key={`${i}-${j}`}
                      x1={`${node.x}%`}
                      y1={`${node.y}%`}
                      x2={`${target.x}%`}
                      y2={`${target.y}%`}
                      stroke={isActive ? "#ef4444" : "#374151"}
                      strokeWidth={isActive ? "2" : "1"}
                      className="transition-all duration-500"
                    />
                  );
                })
              )}
            </svg>
            
            {/* Nodes */}
            {nodes.map((node) => {
              const isActive = activeNodes.includes(node.id);
              return (
                <div
                  key={node.id}
                  className="absolute w-4 h-4 rounded-full transition-all duration-500"
                  style={{
                    left: `${node.x}%`,
                    top: `${node.y}%`,
                    backgroundColor: isActive ? "#ef4444" : "#4b5563",
                    boxShadow: isActive ? "0 0 20px rgba(239, 68, 68, 0.6)" : "none",
                    transform: isActive ? "scale(1.5)" : "scale(1)",
                  }}
                />
              );
            })}
            
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-t from-red-500/5 to-transparent pointer-events-none" />
          </div>
          
          {/* Content */}
          <div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Your Brain,<br />
              Optimized
            </h2>
            <p className="text-gray-400 text-lg mb-6">
              Here's the thing: you forget most of what you learn. Not because you're bad at learning, but because your brain naturally clears out information you don't use.
            </p>
            <p className="text-gray-400 text-lg mb-6">
              Spaced repetition works with this reality. It shows you information right before you'd forget it—so your brain says "okay, this must be important" and holds onto it longer.
            </p>
            <p className="text-gray-400 text-lg">
              Do this enough times, and what used to slip away becomes permanent.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

