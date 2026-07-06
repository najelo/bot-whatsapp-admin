'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';
import { getNodeStyle, nodeConfig } from './NodeStyles';
import 'reactflow/dist/style.css';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  useEffect(() => {
    const load = async () => {
      const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) setNodes(data.nodes || []);
    };
    load();
  }, []);

  const saveToDb = async () => {
    await supabase.from('nodos').upsert({ id: 'flow_principal', nodes });
    alert('Guardado');
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#050505', color: 'white' }}>
      <aside style={{ width: '250px', background: '#0f0f12', padding: '20px' }}>
        <h2>SendyPRO</h2>
        {Object.keys(nodeConfig).map(t => (
          <button key={t} onClick={() => setNodes([...nodes, { id: Date.now().toString(), data: { label: t }, position: { x: 50, y: 50 } }])} style={{ display: 'block', width: '100%', margin: '5px 0' }}>+ {t}</button>
        ))}
        <button onClick={saveToDb} style={{ marginTop: '20px', width: '100%', background: '#2563eb' }}>💾 Guardar Flujo</button>
      </aside>
      
      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow 
          nodes={nodes.map(n => ({ ...n, style: getNodeStyle(n.data.label) }))}
          onNodeClick={(_, n) => setSelectedNodeId(n.id)}
        />
        
        {selectedNodeId && (
          <div style={{ position: 'absolute', right: 0, top: 0, width: '300px', height: '100%', zIndex: 10 }}>
            <FlowEditor 
              node={nodes.find(n => n.id === selectedNodeId)} 
              onUpdate={(id, data) => setNodes(nodes.map(n => n.id === id ? { ...n, data } : n))}
              onClose={() => setSelectedNodeId(null)}
            />
          </div>
        )}
      </main>
    </div>
  );
}
