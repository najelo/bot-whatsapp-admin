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
  const [activeView, setActiveView] = useState('flujos'); // Gestiona qué parte del menú está abierta
  const [nodes, setNodes] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  const menuItems = [
    { id: 'flujos', label: 'Flujos', icon: '🚀' },
    { id: 'pagos', label: 'Pagos', icon: '💳' },
    { id: 'logs', label: 'Logs', icon: '📜' },
    { id: 'config', label: 'Configuración', icon: '⚙️' }
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#050505', color: 'white' }}>
      {/* Menú Lateral Profesional */}
      <aside style={{ width: '250px', background: '#0f0f12', padding: '20px', borderRight: '1px solid #27272a' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '30px' }}>SendyPRO Admin</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {menuItems.map(item => (
            <button 
              key={item.id} 
              onClick={() => setActiveView(item.id)}
              style={{ ...navButtonStyle, background: activeView === item.id ? '#27272a' : 'transparent' }}
            >
              {item.icon} {item.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Contenido Dinámico según la selección */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        {activeView === 'flujos' ? (
          <>
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
          </>
        ) : (
          <div style={{ padding: '40px' }}>
            <h1>Sección: {activeView.toUpperCase()}</h1>
            <p>Próximamente disponible en esta vista.</p>
          </div>
        )}
      </main>
    </div>
  );
}

const navButtonStyle = {
  width: '100%', padding: '12px', textAlign: 'left', borderRadius: '8px',
  border: 'none', color: '#a1a1aa', cursor: 'pointer', transition: '0.2s'
};
