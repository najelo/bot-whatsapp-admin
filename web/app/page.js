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

  // 1. CARGAR FLUJO AL INICIAR
  useEffect(() => {
    const loadFlow = async () => {
      const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) {
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
      }
    };
    loadFlow();
  }, []);

  // 2. GUARDAR FLUJO EN SUPABASE
  const saveFlow = async () => {
    const { error } = await supabase.from('nodos').upsert({ id: 'flow_principal', nodes, edges });
    if (error) alert('Error: ' + error.message);
    else alert('¡Flujo guardado con éxito!');
  };

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '', media: '', delay: '' },
      position: { x: Math.random() * 300, y: Math.random() * 300 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0b', color: 'white' }}>
      <aside style={{ width: '250px', background: '#1c1c1f', padding: '20px' }}>
        <h3>Componentes</h3>
        {['Texto', 'Imagen', 'Video', 'Audio', 'PDF', 'Esperar'].map(t => (
          <button key={t} onClick={() => addNode(t)} style={btnStyle}>+ {t}</button>
        ))}
        <button onClick={saveFlow} style={{...btnStyle, background: '#4f46e5', marginTop: '20px'}}>💾 Guardar en BD</button>
      </aside>

      <div style={{ flexGrow: 1 }}>
        <ReactFlow 
          nodes={nodes} 
          edges={edges} 
          onNodesChange={(changes) => setNodes((nds) => applyNodeChanges(changes, nds))}
          onNodeClick={(_, n) => setSelectedNode(n)} 
        />
      </div>

      {selectedNode && (
        <div style={{ width: '300px', background: '#1c1c1f', borderLeft: '1px solid #333' }}>
          <FlowEditor node={selectedNode} onUpdate={(id, data) => setNodes(nodes.map(n => n.id === id ? {...n, data} : n))} onClose={() => setSelectedNode(null)} />
        </div>
      )}
    </div>
  );
}

const btnStyle = { width: '100%', padding: '10px', marginBottom: '8px', background: '#333', border: 'none', color: 'white', cursor: 'pointer' };
