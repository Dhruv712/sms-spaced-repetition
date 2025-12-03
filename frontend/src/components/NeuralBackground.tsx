import { useEffect, useState } from "react";

export const NeuralBackground: React.FC = () => {
  const [activeNodes, setActiveNodes] = useState<number[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const randomNodes = Array.from(
        { length: 5 },
        () => Math.floor(Math.random() * 20)
      );
      setActiveNodes(randomNodes);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const nodes = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: ((i % 10) * 10) + 5, // 10 columns
    y: Math.floor(i / 10) * 40 + 10, // 2 rows
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
      <svg className="w-full h-full">
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
                stroke={isActive ? "#ff4c3d" : "#1f2937"}
                strokeWidth={isActive ? 1.5 : 0.75}
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
            className="absolute w-2 h-2 rounded-full"
            style={{
              left: `${node.x}%`,
              top: `${node.y}%`,
              backgroundColor: isActive ? "#ff4c3d" : "#4b5563",
              boxShadow: isActive
                ? "0 0 18px rgba(255, 76, 61, 0.6)"
                : "none",
              transform: isActive ? "scale(1.4)" : "scale(1)",
              transition: "all 400ms ease-out",
            }}
          />
        );
      })}
    </div>
  );
};


