'use client';
import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL || '', process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '');

export default function Home() {
  const [nodes, setNodes] = useState([{ id: '1', data: { label: 'Inicio', text: '', media: '', delay: '' }, position: { x: 250, y: 50 } }]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '', media: '', delay: '' },
      position: { x: Math.random() * 200, y: Math.random() * 200 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const updateNodeData = (id, key, value) => {
    setNodes((nds) => nds.map((n) => n.id === id ? { ...n, data: { ...n.data, [key]: value } } : n));
    if (selectedNode) setSelectedNode({ ...selectedNode, data: { ...selectedNode.data, [key]: value } });
  };

  const saveFlow = async () => {
    const { error } = await supabase.from('nodos').upsert({ id: 'flow_principal', nodes, edges });
    alert(error ? 'Error: ' + error.message : '¡Guardado correctamente!');
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0b', color: 'white' }}>
      <aside style={{ width: '220px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
        <h3>Componentes</h3>
        {['Texto', 'Imagen', 'Video', 'Audio', 'PDF', 'Esperar'].map(t => (
          <button key={t} onClick={() => addNode(t)} style={btnStyle}>+ Nodo {t}</button>
        ))}
        <button onClick={saveFlow} style={{...btnStyle, background: '#4f46e5', marginTop: '20px'}}>💾 Guardar</button>
      </aside>

      <div style={{ flexGrow: 1 }}>
        <ReactFlow nodes={nodes} edges={edges} onNodeClick={(e, n) => setSelectedNode(n)} />
      </div>

      {selectedNode && (
        <div style={{ width: '300px', borderLeft: '1px solid #333' }}>
          <FlowEditor selectedNode={selectedNode} onUpdate={updateNodeData} onClose={() => setSelectedNode(null)} />
        </div>
      )}
    </div>
  );
}

const btnStyle = { background: '#333', color: 'white', border: 'none', padding: '10px', width: '100%', marginBottom: '10px', cursor: 'pointer' };
