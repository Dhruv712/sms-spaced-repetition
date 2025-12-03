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
    <div className="relative h-72 md:h-80 rounded-2xl bg-gradient-to-br from-gray-900 to-black border border-gray-800 p-8 overflow-hidden">
      {/* Connection lines */}
      <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.3 }}>
        {nodes.map((node, i) =>
          nodes.slice(i + 1).map((target, j) => {
            const isActive =
              activeNodes.includes(node.id) && activeNodes.includes(target.id);
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
            className="absolute w-3 h-3 md:w-4 md:h-4 rounded-full transition-all duration-500"
            style={{
              left: `${node.x}%`,
              top: `${node.y}%`,
              backgroundColor: isActive ? "#ef4444" : "#4b5563",
              boxShadow: isActive
                ? "0 0 20px rgba(239, 68, 68, 0.6)"
                : "none",
              transform: isActive ? "scale(1.5)" : "scale(1)",
            }}
          />
        );
      })}

      {/* Glow effect */}
      <div className="absolute inset-0 bg-gradient-to-t from-red-500/5 to-transparent pointer-events-none" />
    </div>
  );
}

