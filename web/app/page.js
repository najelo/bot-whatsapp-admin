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

  // FUNCIÓN: Cargar flujos desde Supabase
  const loadNodes = async () => {
    const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
    if (data) setNodes(data.nodes);
  };

  // FUNCIÓN: Guardar flujos en Supabase
  const saveToDb = async () => {
    await supabase.from('nodos').upsert({ id: 'flow_principal', nodes });
    alert('Flujo guardado con éxito');
  };

  useEffect(() => { loadNodes(); }, []);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <aside style={{ width: '260px', background: '#111', color: '#fff', padding: '20px' }}>
        <button onClick={saveToDb} style={{ width: '100%', background: 'green' }}>💾 Guardar en DB</button>
        <button onClick={() => setNodes([...nodes, { id: Date.now().toString(), data: { label: 'Nuevo Nodo' }, position: { x: 50, y: 50 } }])} style={{ width: '100%', marginTop: '10px' }}>+ Agregar Nodo</button>
      </aside>

      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow nodes={nodes} onNodeClick={(_, n) => setSelectedNode(n)} />
      </main>

      {selectedNode && (
        <aside style={{ width: '320px' }}>
          <FlowEditor 
            node={selectedNode} 
            onUpdate={(id, data) => setNodes(nodes.map(n => n.id === id ? { ...n, data } : n))}
            onClose={() => setSelectedNode(null)} 
          />
        </aside>
      )}
    </div>
  );
}
