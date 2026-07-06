'use client';

import React, { useState, useCallback } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  Controls, 
  MiniMap, 
  applyEdgeChanges, 
  applyNodeChanges 
} from 'reactflow';
import 'reactflow/dist/style.css';

// Nodos iniciales
const initialNodes = [
  { id: '1', type: 'input', data: { label: 'Inicio del Bot' }, position: { x: 250, y: 50 } },
];

export default function Home() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState([]);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );
  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#0f0f11' }}>
      {/* Sidebar Lateral */}
      <aside style={{ width: '250px', background: '#1c1c1f', color: 'white', padding: '20px', borderRight: '1px solid #333' }}>
        <h2 style={{ fontSize: '1.2rem', marginBottom: '20px' }}>Componentes</h2>
        <div style={{ padding: '10px', background: '#2d2d31', borderRadius: '8px', cursor: 'pointer' }}>
          + Arrastrar Nodo de Texto
        </div>
      </aside>

      {/* Área del Lienzo */}
      <div style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background color="#333" gap={20} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
