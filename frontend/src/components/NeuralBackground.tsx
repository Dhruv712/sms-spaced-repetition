import { useEffect, useState } from "react";

export const NeuralBackground: React.FC = () => {
  const [activeNodes, setActiveNodes] = useState<number[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const randomNodes = Array.from(
        { length: 7 },
        () => Math.floor(Math.random() * 40)
      );
      setActiveNodes(randomNodes);
    }, 2600);

    return () => clearInterval(interval);
  }, []);

  const cols = 8;
  const rows = 5;
  const nodes = Array.from({ length: cols * rows }, (_, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    return {
      id: i,
      x: (col / (cols - 1)) * 100,
      y: (row / (rows - 1)) * 100,
    };
  });

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-40">
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
                stroke={isActive ? "#ff4c3d" : "#020617"}
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
              transition: "all 700ms ease-out",
            }}
          />
        );
      })}
    </div>
  );
};


