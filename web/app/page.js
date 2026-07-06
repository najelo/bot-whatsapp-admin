'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';

// Cargamos ReactFlow solo en el cliente para evitar errores de renderizado
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '', 
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
);

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('flujos');
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  // Cargar flujo desde Supabase
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

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '', media: '' },
      position: { x: Math.random() * 200, y: Math.random() * 200 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const updateNodeData = (id, newData) => {
    setNodes((nds) => nds.map((n) => n.id === id ? { ...n, data: { ...n.data, ...newData } } : n));
    if (selectedNode) setSelectedNode({ ...selectedNode, data: { ...selectedNode.data, ...newData } });
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#050505', color: '#fff' }}>
      {/* Sidebar Lateral */}
      <aside style={{ width: '260px', background: '#0f0f12', padding: '20px', borderRight: '1px solid #27272a' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '30px' }}>SendyPRO Admin</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button onClick={() => setActiveTab('flujos')} style={tabStyle(activeTab === 'flujos')}>🚀 Flujos</button>
          <button onClick={() => setActiveTab('pagos')} style={tabStyle(activeTab === 'pagos')}>💳 Pagos</button>
          <button onClick={() => setActiveTab('logs')} style={tabStyle(activeTab === 'logs')}>📜 Logs</button>
        </nav>

        {activeTab === 'flujos' && (
          <div style={{ marginTop: '40px' }}>
            <h4 style={{ color: '#71717a', fontSize: '12px', textTransform: 'uppercase' }}>Componentes</h4>
            {['Texto', 'Imagen', 'Audio', 'Video', 'PDF', 'Esperar'].map(t => (
              <button key={t} onClick={() => addNode(t)} style={btnStyle}>+ {t}</button>
            ))}
          </div>
        )}
      </aside>

      {/* Área Principal */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        {activeTab === 'flujos' ? (
          <ReactFlow 
            nodes={nodes} 
            edges={edges} 
            onNodeClick={(_, n) => setSelectedNode(n)} 
            style={{ background: '#0a0a0b' }}
          />
        ) : (
          <div style={{ padding: '40px' }}><h2>Sección {activeTab}</h2></div>
        )}

        {/* Panel de edición lateral */}
        {selectedNode && (
          <div style={{ position: 'absolute', right: 0, top: 0, width: '300px', height: '100%', background: '#0f0f12', borderLeft: '1px solid #27272a', zIndex: 10 }}>
            <FlowEditor node={selectedNode} onUpdate={updateNodeData} onClose={() => setSelectedNode(null)} />
          </div>
        )}
      </main>
    </div>
  );
}

// Estilos
const tabStyle = (active) => ({
  background: active ? '#27272a' : 'transparent',
  color: active ? '#fff' : '#a1a1aa',
  border: 'none', padding: '12px', textAlign: 'left', borderRadius: '8px', cursor: 'pointer', transition: '0.2s'
});

const btnStyle = { width: '100%', padding: '10px', marginTop: '8px', background: '#18181b', border: '1px solid #27272a', color: '#fff', borderRadius: '6px', cursor: 'pointer' };
