import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';
import ForceGraph2D from 'react-force-graph-2d';

interface KnowledgeNode {
  id: number;
  concept: string;
  definition: string;
  tags: string[];
  deck_id: number | null;
  deck_name: string | null;
  accuracy: number | null;  // 0-100 or null if no reviews
  x: number;
  y: number;
  vx?: number;  // Velocity x (added by D3 force simulation)
  vy?: number;  // Velocity y (added by D3 force simulation)
}

interface KnowledgeLink {
  source: number;
  target: number;
  value: number;
}

const KnowledgeMap: React.FC = () => {
  const { token } = useAuth();
  const [data, setData] = useState<{ nodes: KnowledgeNode[]; links: KnowledgeLink[] }>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const [deckAttraction, setDeckAttraction] = useState(1.0);
  const [tagAttraction, setTagAttraction] = useState(0.5);
  const [invertAccuracy, setInvertAccuracy] = useState(false);
  const fgRef = useRef<any>(null);

  // Fetch data only once (don't refetch when sliders change)
  useEffect(() => {
    if (!token) return;

    const fetchKnowledgeMap = async () => {
      try {
        const response = await axios.get(buildApiUrl('/dashboard/knowledge-map'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          // Don't pass slider params to backend - we'll handle forces on frontend
        });
        
        // Ensure links reference node objects, not just IDs
        const nodes = response.data.nodes || [];
        const nodeMap = new Map(nodes.map((node: any) => [node.id, node]));
        const links = (response.data.links || []).map((link: any) => ({
          ...link,
          source: typeof link.source === 'number' ? nodeMap.get(link.source) : link.source,
          target: typeof link.target === 'number' ? nodeMap.get(link.target) : link.target,
        }));
        
        setData({ nodes, links });
      } catch (err) {
        console.error('Error fetching knowledge map:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchKnowledgeMap();
  }, [token]); // Only fetch when token changes, not when sliders change

  // Restart simulation when forces change (but don't reset zoom)
  useEffect(() => {
    if (fgRef.current && data.nodes.length > 0) {
      // Access the d3 simulation and update force parameters
      const simulation = fgRef.current.d3Force();
      if (simulation) {
        // Update charge force strength (repulsion - higher = more spread out)
        // Make it much stronger - this controls general node spacing
        const charge = simulation.force('charge');
        if (charge) {
          // Base repulsion, stronger when deck attraction is higher
          charge.strength(-300 * (1 + deckAttraction));  // Much stronger base repulsion
        }
        
        // Add a custom force for deck-based clustering
        // Remove old deck force if it exists
        simulation.force('deck-cluster', null);
        
        // Create deck-based clustering force
        const deckClusterForce = (alpha: number) => {
          const nodes = data.nodes;
          for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
              const node1 = nodes[i];
              const node2 = nodes[j];
              
              // If same deck, apply strong attraction
              if (node1.deck_id && node2.deck_id && node1.deck_id === node2.deck_id) {
                const dx = (node2.x || 0) - (node1.x || 0);
                const dy = (node2.y || 0) - (node1.y || 0);
                const dist = Math.sqrt(dx * dx + dy * dy) || 0.1;
                
                // Strong attraction force based on slider
                const force = deckAttraction * 50 * alpha;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                
                node1.vx = (node1.vx || 0) + fx;
                node1.vy = (node1.vy || 0) + fy;
                node2.vx = (node2.vx || 0) - fx;
                node2.vy = (node2.vy || 0) - fy;
              }
            }
          }
        };
        
        simulation.force('deck-cluster', deckClusterForce);
        
        // Update link force distance and strength for tag-based attraction
        const link = simulation.force('link');
        if (link) {
          link.distance((linkData: any) => {
            const baseDistance = 100;
            const similarity = linkData.value || 0;
            // Higher tag attraction = shorter links = stronger clustering
            return baseDistance - (tagAttraction * similarity * 80);
          });
          link.strength((linkData: any) => {
            // Higher tag attraction = stronger link force
            return tagAttraction * (linkData.value || 0.5) * 2;
          });
        }
        
        // Restart simulation with new parameters (but don't zoom)
        simulation.alpha(1).restart();  // Use full alpha for stronger effect
      }
    }
  }, [deckAttraction, tagAttraction, data]);

  if (loading) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (data.nodes.length === 0) {
    return (
      <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Knowledge Map</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No flashcards available. Create some flashcards with tags to see your knowledge map.
        </p>
      </div>
    );
  }

  // Color nodes by deck
  const getNodeColor = (node: KnowledgeNode) => {
    if (node.deck_id) {
      // Generate a color based on deck_id
      const hue = (node.deck_id * 137.508) % 360; // Golden angle for color distribution
      return `hsl(${hue}, 70%, 50%)`;
    }
    return '#9ca3af'; // Gray for cards without decks
  };

  // Get unique decks for legend
  const deckMap = new Map<number, { name: string; color: string }>();
  data.nodes.forEach((node) => {
    if (node.deck_id && node.deck_name && !deckMap.has(node.deck_id)) {
      deckMap.set(node.deck_id, {
        name: node.deck_name,
        color: getNodeColor(node)
      });
    }
  });
  const deckLegend = Array.from(deckMap.values());

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Knowledge Map</h2>
      <div className="mb-4">
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
          2D visualization of your flashcards. Cards with similar tags (added when creating/editing flashcards) are positioned closer together.
          Click and drag nodes, scroll to zoom.
        </p>
        {deckLegend.length > 0 && (
          <div className="flex flex-wrap gap-3 items-center">
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Decks:</span>
            {deckLegend.map((deck, index) => (
              <div key={index} className="flex items-center gap-1.5">
                <div 
                  className="w-3 h-3 rounded-full border border-gray-300 dark:border-gray-600"
                  style={{ backgroundColor: deck.color }}
                />
                <span className="text-xs text-gray-600 dark:text-gray-400">{deck.name}</span>
              </div>
            ))}
            {data.nodes.some(n => !n.deck_id) && (
              <div className="flex items-center gap-1.5">
                <div 
                  className="w-3 h-3 rounded-full border border-gray-300 dark:border-gray-600"
                  style={{ backgroundColor: '#9ca3af' }}
                />
                <span className="text-xs text-gray-600 dark:text-gray-400">No deck</span>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Force controls */}
      <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Deck Clustering: {deckAttraction.toFixed(1)}
            </label>
            <input
              type="range"
              min="0"
              max="3"
              step="0.1"
              value={deckAttraction}
              onChange={(e) => setDeckAttraction(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tag Attraction: {tagAttraction.toFixed(1)}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={tagAttraction}
              onChange={(e) => setTagAttraction(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
          </div>
          <div className="flex items-center">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={invertAccuracy}
                onChange={(e) => setInvertAccuracy(e.target.checked)}
                className="mr-2 w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                Invert Size (lower accuracy = bigger)
              </span>
            </label>
          </div>
        </div>
      </div>
      
      <div className="relative bg-gray-50 dark:bg-gray-950 rounded border border-gray-200 dark:border-gray-700 overflow-hidden" style={{ height: '600px', width: '100%' }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={data}
          nodeLabel={(node: any) => `${node.concept || 'Unknown'}`}
          nodeColor={(node: any) => getNodeColor(node)}
          nodeVal={(node: any) => {
            // Node size based on accuracy (if available)
            if (node.accuracy !== null && node.accuracy !== undefined) {
              // Map accuracy (0-100) to size (5-20)
              const baseSize = 5;
              const maxSize = 20;
              const accuracyValue = invertAccuracy ? (100 - node.accuracy) : node.accuracy;
              return baseSize + (accuracyValue / 100) * (maxSize - baseSize);
            }
            return 10; // Default size for cards without reviews
          }}
          nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const label = node.concept || '';
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // Calculate node size based on accuracy
            let nodeSize = 8; // Default
            if (node.accuracy !== null && node.accuracy !== undefined) {
              const baseSize = 5;
              const maxSize = 20;
              const accuracyValue = invertAccuracy ? (100 - node.accuracy) : node.accuracy;
              nodeSize = baseSize + (accuracyValue / 100) * (maxSize - baseSize);
            }
            
            ctx.fillStyle = node.id === selectedNode?.id ? '#3b82f6' : getNodeColor(node);
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI, false);
            ctx.fill();
            
            // Draw label
            ctx.fillStyle = '#333';
            ctx.fillText(label, node.x, node.y + nodeSize + 5);
          }}
          linkColor={() => 'rgba(150, 150, 150, 0.3)'}
          linkWidth={(link: any) => (link.value || 0.5) * 2}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkDirectionalArrowColor={() => 'rgba(150, 150, 150, 0.3)'}
          onNodeClick={(node: any) => {
            setSelectedNode(node);
          }}
          onNodeHover={(node: any) => {
            // Change cursor on hover
            if (node) {
              document.body.style.cursor = 'pointer';
            } else {
              document.body.style.cursor = 'default';
            }
          }}
          onNodeDrag={(node: any) => {
            node.fx = node.x;
            node.fy = node.y;
          }}
          onNodeDragEnd={(node: any) => {
            node.fx = null;
            node.fy = null;
          }}
          cooldownTicks={100}
        />
        
        {/* Node details overlay in top-right */}
        {selectedNode && (
          <div 
            className="absolute top-4 right-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg p-4 max-w-sm z-10"
            style={{ maxHeight: '400px', overflowY: 'auto' }}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                {selectedNode.deck_name && (
                  <span className="inline-block px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded mb-2">
                    {selectedNode.deck_name}
                  </span>
                )}
                <h3 className="text-sm font-medium text-gray-900 dark:text-darktext mb-2">
                  {selectedNode.concept}
                </h3>
                <div className="text-xs text-gray-700 dark:text-gray-300 mb-2">
                  <strong>Definition:</strong>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-3 whitespace-pre-wrap">
                  {selectedNode.definition}
                </div>
                {selectedNode.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {selectedNode.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="ml-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-sm"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
};

export default KnowledgeMap;

