'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';
import { getNodeStyle, nodeConfig } from './NodeStyles';
import 'reactflow/dist/style.css';

// Importante: ReactFlow solo debe cargar en el cliente para evitar errores SSR
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL, 
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  // Cargar nodos al iniciar
  useEffect(() => {
    const loadNodes = async () => {
      const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) setNodes(data.nodes || []);
    };
    loadNodes();
  }, []);

  // Guardar cambios en Supabase
  const saveToDb = async () => {
    await supabase.from('nodos').upsert({ id: 'flow_principal', nodes });
    alert('Flujo guardado correctamente');
  };

  // Agregar nuevo nodo al lienzo
  const addNode = (type) => {
    const newNode = { 
      id: Date.now().toString(), 
      data: { label: type, content: '', delay: 0 }, 
      position: { x: 100, y: 100 } 
    };
    setNodes([...nodes, newNode]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#09090b', color: '#f4f4f5' }}>
      {/* Sidebar Lateral */}
      <aside style={{ width: '260px', background: '#0f0f12', padding: '20px', borderRight: '1px solid #27272a' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '20px' }}>SendyPRO Admin</h2>
        
        <button onClick={saveToDb} className="sidebar-btn" style={{ background: '#166534', color: 'white' }}>💾 Guardar en DB</button>
        
        <h4 style={{ color: '#52525b', fontSize: '11px', textTransform: 'uppercase', marginTop: '30px' }}>Agregar Nodo</h4>
        {Object.keys(nodeConfig).map(t => (
          <button key={t} className="sidebar-btn" onClick={() => addNode(t)}>
            + {t}
          </button>
        ))}
      </aside>

      {/* Lienzo Principal */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow 
          nodes={nodes.map(n => ({ ...n, style: getNodeStyle(n.data.label) }))}
          onNodeClick={(_, n) => setSelectedNode(n)}
        />
      </main>

      {/* Editor Lateral */}
      {selectedNode && (
        <aside style={{ width: '350px' }}>
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
