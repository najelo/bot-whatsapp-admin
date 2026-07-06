'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function FlowBuilder() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '', media: '' },
      position: { x: 100, y: 100 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar de Componentes */}
      <aside style={{ width: '250px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
        <h2 style={{ fontSize: '18px' }}>SendyPRO Admin</h2>
        {['Texto', 'Imagen', 'Video', 'Audio', 'PDF'].map(t => (
          <button key={t} onClick={() => addNode(t)} style={btnStyle}>+ {t}</button>
        ))}
      </aside>

      {/* Canvas */}
      <div style={{ flexGrow: 1 }}>
        <ReactFlow nodes={nodes} edges={edges} onNodeClick={(_, n) => setSelectedNode(n)} />
      </div>

      {/* Panel de Edición */}
      {selectedNode && (
        <div style={{ width: '300px', background: '#1c1c1f', borderLeft: '1px solid #333' }}>
          <FlowEditor node={selectedNode} onClose={() => setSelectedNode(null)} />
        </div>
      )}
    </div>
  );
}

const btnStyle = { width: '100%', padding: '10px', marginBottom: '8px', background: '#333', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' };
