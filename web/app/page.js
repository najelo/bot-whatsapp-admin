'use client';
import React, { useState, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';

// Importación dinámica para evitar error de "window is not defined" en Vercel
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '', 
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
);

export default function Home() {
  const [activeView, setActiveView] = useState('flow-builder');
  const [nodes, setNodes] = useState([{ id: '1', data: { label: 'Inicio', text: '', media: '', delay: '' }, position: { x: 250, y: 50 } }]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '', media: '', delay: '' },
      position: { x: Math.random() * 300, y: Math.random() * 300 },
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

  if (activeView !== 'flow-builder') return <div style={{ color: 'white', padding: '20px' }}>Sección {activeView}</div>;

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0b', color: 'white' }}>
      <aside style={{ width: '220px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
        <h3>Componentes</h3>
        {['Texto', 'Imagen', 'Esperar'].map(t => <button key={t} onClick={() => addNode(t)} style={btnStyle}>+ Nodo {t}</button>)}
        <button onClick={saveFlow} style={{...btnStyle, background: '#4f46e5', marginTop: '20px'}}>💾 Guardar</button>
      </aside>

      <div style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={(c) => setNodes((nds) => import('reactflow').then(rf => rf.applyNodeChanges(c, nds)))} onNodeClick={(e, n) => setSelectedNode(n)}>
          <button style={{ position: 'absolute', top: 10, left: 10, zIndex: 10 }} onClick={() => setNodes([])}>Limpiar Lienzo</button>
        </ReactFlow>
      </div>

      {selectedNode && (
        <div style={{ width: '300px', background: '#1c1c1f', padding: '20px', borderLeft: '1px solid #333' }}>
          <h3>Editar {selectedNode.data.label}</h3>
          <textarea value={selectedNode.data.text} onChange={(e) => updateNodeData(selectedNode.id, 'text', e.target.value)} style={inputStyle} />
          {selectedNode.data.label === 'Imagen' && <input type="text" placeholder="URL imagen" onChange={(e) => updateNodeData(selectedNode.id, 'media', e.target.value)} style={inputStyle} />}
          <button onClick={() => { setNodes(nds => nds.filter(n => n.id !== selectedNode.id)); setSelectedNode(null); }} style={{ background: '#ff4d4d', border: 'none', padding: '10px', width: '100%' }}>Borrar Nodo</button>
        </div>
      )}
    </div>
  );
}

const btnStyle = { background: '#333', color: 'white', border: 'none', padding: '10px', width: '100%', marginBottom: '10px', cursor: 'pointer' };
const inputStyle = { width: '100%', background: '#333', color: 'white', padding: '8px', marginBottom: '10px' };
