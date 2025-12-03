import { useEffect, useState } from "react";

// Hero background neural visualization, tuned to feel like the standalone card
export const NeuralBackground: React.FC = () => {
  const [activeNodes, setActiveNodes] = useState<number[]>([]);

  // Similar timing/behavior to the standalone visualization (soft, periodic pulses)
  useEffect(() => {
    const interval = setInterval(() => {
      const randomNodes = Array.from(
        { length: 5 },
        () => Math.floor(Math.random() * 12)
      );
      setActiveNodes(randomNodes);
    }, 2200);

    return () => clearInterval(interval);
  }, []);

  // 4x3 grid of nodes spread across hero
  const nodes = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    x: (i % 4) * 33.33,
    y: Math.floor(i / 4) * 33.33 + 10, // slight vertical padding
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-35">
      <svg className="w-full h-full">
        {nodes.map((node, i) =>
          nodes.slice(i + 1).map((target, j) => {
            // Only draw some connections to keep it light
            if ((i + j) % 2 !== 0) return null;
            const isActive =
              activeNodes.includes(node.id) && activeNodes.includes(target.id);
            return (
              <line
                key={`${i}-${j}`}
                x1={`${node.x}%`}
                y1={`${node.y}%`}
                x2={`${target.x}%`}
                y2={`${target.y}%`}
                stroke={isActive ? "#ff4c3d" : "#111827"}
                strokeWidth={isActive ? 1.6 : 0.6}
                style={{
                  transition: "stroke 700ms ease-out, stroke-width 700ms ease-out",
                }}
              />
            );
          })
        )}
      </svg>
      {nodes.map((node) => {
        const isActive = activeNodes.includes(node.id);
        return (
          <div
            key={node.id}
            className="absolute rounded-full"
            style={{
              width: "0.7rem",
              height: "0.7rem",
              left: `${node.x}%`,
              top: `${node.y}%`,
              marginLeft: "-0.35rem",
              marginTop: "-0.35rem",
              backgroundColor: isActive ? "#ff4c3d" : "#4b5563",
              boxShadow: isActive
                ? "0 0 20px rgba(255, 76, 61, 0.7)"
                : "none",
              transform: isActive ? "scale(1.6)" : "scale(1)",
              transition:
                "transform 700ms ease-out, box-shadow 700ms ease-out, background-color 700ms ease-out",
            }}
          />
        );
      })}
    </div>
  );
};

