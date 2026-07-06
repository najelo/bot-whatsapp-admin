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
  const [activeView, setActiveView] = useState('flujos');
  const [nodes, setNodes] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  // Carga inicial
  useEffect(() => {
    const load = async () => {
      const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) setNodes(data.nodes || []);
    };
    load();
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#050505', color: 'white' }}>
      {/* Sidebar */}
      <aside style={{ width: '250px', background: '#0f0f12', padding: '20px' }}>
        <h2>SendyPRO</h2>
        {['flujos', 'pagos', 'logs'].map(view => (
          <button key={view} onClick={() => setActiveView(view)} style={{ display: 'block', width: '100%', margin: '10px 0', padding: '10px' }}>
            {view.toUpperCase()}
          </button>
        ))}
        {activeView === 'flujos' && (
          <div style={{ marginTop: '20px' }}>
            {Object.keys(nodeConfig).map(t => (
              <button key={t} onClick={() => setNodes([...nodes, { id: Date.now().toString(), data: { label: t, contents: [] }, position: { x: 50, y: 50 } }])} style={{ width: '100%' }}>+ {t}</button>
            ))}
          </div>
        )}
      </aside>

      {/* Área Principal - Mantenemos el lienzo siempre presente */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        {/* Contenedor del Lienzo */}
        <div style={{ display: activeView === 'flujos' ? 'block' : 'none', height: '100%' }}>
          <ReactFlow 
            nodes={nodes.map(n => ({ ...n, style: getNodeStyle(n.data.label) }))}
            onNodeClick={(_, n) => setSelectedNodeId(n.id)}
          />
        </div>

        {/* Contenedor de otras secciones */}
        {activeView !== 'flujos' && (
          <div style={{ padding: '40px' }}><h1>Sección {activeView}</h1></div>
        )}

        {/* Editor (Sidebar derecho) */}
        {selectedNodeId && activeView === 'flujos' && (
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
