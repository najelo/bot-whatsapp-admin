'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';
import 'reactflow/dist/style.css';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    const fetchNodes = async () => {
      const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) setNodes(data.nodes || []);
    };
    fetchNodes();
  }, []);

  const saveToDb = async () => {
    await supabase.from('nodos').upsert({ id: 'flow_principal', nodes });
    alert('Flujo guardado con éxito');
  };

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, content: '', delay: 0, checkPayment: false },
      position: { x: Math.random() * 300, y: Math.random() * 300 },
    };
    setNodes([...nodes, newNode]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#000', color: '#fff' }}>
      <aside style={{ width: '260px', background: '#111', padding: '20px', borderRight: '1px solid #333' }}>
        <h2>SendyPRO Admin</h2>
        <button onClick={saveToDb} style={{ width: '100%', padding: '10px', background: '#166534', color: 'white', border: 'none' }}>💾 Guardar Flujo</button>
        <h4 style={{ marginTop: '30px' }}>AGREGAR NODO</h4>
        {['Texto', 'Imagen', 'Audio', 'Video', 'PDF'].map(t => (
          <button key={t} onClick={() => addNode(t)} style={{ display: 'block', width: '100%', margin: '5px 0', padding: '10px', background: '#222', color: 'white', border: 'none' }}>+ {t}</button>
        ))}
      </aside>

      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow nodes={nodes} onNodeClick={(_, n) => setSelectedNode(n)} />
      </main>

      {selectedNode && (
        <aside style={{ width: '320px' }}>
          <FlowEditor node={selectedNode} onUpdate={(id, data) => setNodes(nodes.map(n => n.id === id ? { ...n, data } : n))} onClose={() => setSelectedNode(null)} />
        </aside>
      )}
    </div>
  );
}
