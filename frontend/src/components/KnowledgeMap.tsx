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
  const fgRef = useRef<any>(null);

  useEffect(() => {
    if (!token) return;

    const fetchKnowledgeMap = async () => {
      try {
        const response = await axios.get(buildApiUrl('/dashboard/knowledge-map'), {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        setData(response.data);
      } catch (err) {
        console.error('Error fetching knowledge map:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchKnowledgeMap();
  }, [token]);

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

  return (
    <div className="bg-white dark:bg-darksurface rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-light text-gray-900 dark:text-darktext mb-4">Knowledge Map</h2>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        2D visualization of your flashcards. Cards with similar tags are positioned closer together.
        Click and drag nodes, scroll to zoom.
      </p>
      
      <div className="relative bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700" style={{ height: '600px', width: '100%' }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={data}
          nodeLabel={(node: any) => `${node.concept}`}
          nodeColor={(node: any) => getNodeColor(node)}
          nodeVal={(node: any) => 8}
          nodeRelSize={6}
          linkColor={() => 'rgba(150, 150, 150, 0.4)'}
          linkWidth={(link: any) => link.value * 2}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={1}
          onNodeClick={(node: any) => {
            setSelectedNode(node);
          }}
          onNodeHover={(node: any) => {
            if (node) {
              // Highlight node
              fgRef.current?.nodeColor((n: any) => 
                n.id === node.id ? '#3b82f6' : getNodeColor(n)
              );
            } else {
              // Reset colors
              fgRef.current?.nodeColor((n: any) => getNodeColor(n));
            }
          }}
          cooldownTicks={100}
          onEngineStop={() => {
            // Center the graph when simulation stops
            if (fgRef.current && data.nodes.length > 0) {
              fgRef.current.zoomToFit(400, 20);
            }
          }}
        />
      </div>

      {selectedNode && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              {selectedNode.deck_name && (
                <span className="inline-block px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded mb-2">
                  {selectedNode.deck_name}
                </span>
              )}
              <h3 className="text-base font-medium text-gray-900 dark:text-darktext mb-1">
                {selectedNode.concept}
              </h3>
              {selectedNode.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
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
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeMap;

