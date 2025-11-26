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
  x: number;
  y: number;
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
  const fgRef = useRef<any>(null);

  useEffect(() => {
    if (!token) return;

    const fetchKnowledgeMap = async () => {
      try {
        const response = await axios.get(buildApiUrl('/dashboard/knowledge-map'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          params: {
            deck_attraction: deckAttraction,
            tag_attraction: tagAttraction
          }
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
  }, [token, deckAttraction, tagAttraction]);

  // Restart simulation when forces change
  useEffect(() => {
    if (fgRef.current && data.nodes.length > 0) {
      // Access the d3 simulation and update force parameters
      const simulation = fgRef.current.d3Force();
      if (simulation) {
        // Update charge force strength (repulsion - higher = more spread out)
        const charge = simulation.force('charge');
        if (charge) {
          charge.strength(-30 * deckAttraction);
        }
        
        // Update link force distance and strength
        const link = simulation.force('link');
        if (link) {
          link.distance((linkData: any) => {
            const baseDistance = 50;
            const similarity = linkData.value || 0;
            return baseDistance - (tagAttraction * similarity * 30);
          });
          link.strength((linkData: any) => {
            return tagAttraction * (linkData.value || 0.5);
          });
        }
        
        // Restart simulation with new parameters
        simulation.alpha(1).restart();
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        </div>
      </div>
      
      <div className="relative bg-gray-50 dark:bg-gray-950 rounded border border-gray-200 dark:border-gray-700 overflow-hidden" style={{ height: '600px', width: '100%' }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={data}
          nodeLabel={(node: any) => `${node.concept || 'Unknown'}`}
          nodeColor={(node: any) => getNodeColor(node)}
          nodeVal={(node: any) => 10}
          nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const label = node.concept || '';
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = node.id === selectedNode?.id ? '#3b82f6' : getNodeColor(node);
            ctx.beginPath();
            ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI, false);
            ctx.fill();
            
            // Draw label
            ctx.fillStyle = '#333';
            ctx.fillText(label, node.x, node.y + 15);
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
          d3Force="charge"
          d3ForceStrength={-30 * deckAttraction}
          cooldownTicks={100}
          onEngineStop={() => {
            // Center the graph when simulation stops
            if (fgRef.current && data.nodes.length > 0) {
              setTimeout(() => {
                fgRef.current?.zoomToFit(400, 20);
              }, 100);
            }
          }}
          key={`${deckAttraction}-${tagAttraction}`}
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

