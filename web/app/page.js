'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';
import { getNodeStyle, nodeConfig } from './NodeStyles';
import 'reactflow/dist/style.css';

// Importamos componentes de ReactFlow necesarios
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });
const { Panel } = require('reactflow'); 

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  // Función para agregar nodo
  const addNode = (type) => {
    const newNode = { 
      id: Date.now().toString(), 
      data: { label: type, contents: [] }, 
      position: { x: Math.random() * 200, y: Math.random() * 200 } 
    };
    setNodes([...nodes, newNode]);
  };

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow 
        nodes={nodes.map(n => ({ ...n, style: getNodeStyle(n.data.label) }))}
        onNodeClick={(_, n) => setSelectedNodeId(n.id)}
      >
        {/* Panel integrado dentro del lienzo */}
        <Panel position="top-left" style={{ background: '#0f0f12', padding: '15px', borderRadius: '8px', border: '1px solid #333' }}>
          <h3 style={{ marginTop: 0, color: 'white' }}>Agregar Nodo</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px' }}>
            {Object.keys(nodeConfig).map(t => (
              <button key={t} onClick={() => addNode(t)} style={btnStyle}>{t}</button>
            ))}
          </div>
        </Panel>
      </ReactFlow>

      {/* Editor Lateral */}
      {selectedNodeId && (
        <div style={{ position: 'absolute', right: 0, top: 0, width: '300px', height: '100%', zIndex: 10 }}>
          <FlowEditor 
            node={nodes.find(n => n.id === selectedNodeId)} 
            onUpdate={(id, data) => setNodes(nodes.map(n => n.id === id ? { ...n, data } : n))}
            onClose={() => setSelectedNodeId(null)}
          />
        </div>
      )}
    </div>
  );
}

const btnStyle = { background: '#2563eb', color: 'white', border: 'none', padding: '8px', borderRadius: '4px', cursor: 'pointer' };
