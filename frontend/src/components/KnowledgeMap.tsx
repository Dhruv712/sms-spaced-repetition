import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buildApiUrl } from '../config';
import axios from 'axios';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';

interface KnowledgeNode {
  id: number;
  concept: string;
  definition: string;
  tags: string[];
  deck_id: number | null;
  deck_name: string | null;
  x: number;
  y: number;
  z: number;
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
  const fgRef = useRef<any>();

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
        3D visualization of your flashcards. Cards with similar tags are positioned closer together.
        Click and drag to rotate, scroll to zoom.
      </p>
      
      <div className="relative" style={{ height: '600px', width: '100%' }}>
        <ForceGraph3D
          ref={fgRef}
          graphData={data}
          nodeLabel={(node: any) => `${node.concept}`}
          nodeColor={(node: any) => getNodeColor(node)}
          nodeOpacity={0.9}
          linkColor={() => 'rgba(100, 100, 100, 0.3)'}
          linkWidth={(link: any) => link.value * 2}
          linkOpacity={0.3}
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
          nodeThreeObject={(node: any) => {
            const sprite = new THREE.Sprite(
              new THREE.SpriteMaterial({
                color: getNodeColor(node),
                sizeAttenuation: false,
              })
            );
            sprite.scale.set(8, 8, 1);
            return sprite;
          }}
          linkThreeObjectExtend={true}
          linkThreeObject={(link: any) => {
            const material = new THREE.LineBasicMaterial({
              color: 'rgba(100, 100, 100, 0.3)',
              opacity: 0.3,
              transparent: true,
            });
            const geometry = new THREE.BufferGeometry().setFromPoints([
              new THREE.Vector3(link.source.x, link.source.y, link.source.z),
              new THREE.Vector3(link.target.x, link.target.y, link.target.z),
            ]);
            return new THREE.Line(geometry, material);
          }}
          showNavInfo={false}
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

