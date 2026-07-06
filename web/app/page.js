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

  // Función para actualizar datos del nodo
  const updateNodeData = (id, newData) => {
    setNodes((nds) => nds.map((n) => n.id === id ? { ...n, data: { ...n.data, ...newData } } : n));
    setSelectedNode((prev) => ({ ...prev, data: { ...prev.data, ...newData } }));
  };

  return (
    <div style={{ height: '100vh', display: 'flex' }}>
      <div style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow 
          nodes={nodes} 
          edges={edges} 
          onNodeClick={(e, n) => setSelectedNode(n)} // ¡Aquí activamos el nodo!
        />
      </div>
      
      {/* Panel lateral de edición */}
      {selectedNode && (
        <div style={{ width: '300px', background: '#1c1c1f', borderLeft: '1px solid #333' }}>
          <FlowEditor 
            selectedNode={selectedNode} 
            onUpdate={updateNodeData} 
            onClose={() => setSelectedNode(null)} 
          />
        </div>
      )}
    </div>
  );
}
