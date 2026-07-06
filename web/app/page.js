// web/app/page.js
'use client';
import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('flujos');
  const [nodes, setNodes] = useState([]);

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type },
      position: { x: Math.random() * 200, y: Math.random() * 200 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar Lateral */}
      <aside style={{ width: '250px', background: '#0f0f12', padding: '20px', borderRight: '1px solid #27272a' }}>
        <h2 style={{ color: '#fff', fontSize: '18px', marginBottom: '20px' }}>SendyPRO Admin</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button onClick={() => setActiveTab('flujos')} style={btnStyle}>🚀 Flujos (Lienzo)</button>
          <button onClick={() => setActiveTab('pagos')} style={btnStyle}>💳 Pagos</button>
          <button onClick={() => setActiveTab('logs')} style={btnStyle}>📜 Logs</button>
        </nav>
        
        {activeTab === 'flujos' && (
          <div style={{ marginTop: '30px' }}>
            <h4 style={{ color: '#a1a1aa' }}>Agregar Nodo</h4>
            {['Texto', 'Imagen', 'Audio', 'Video', 'PDF', 'Esperar'].map(t => (
              <button key={t} onClick={() => addNode(t)} style={nodeBtn}>+ {t}</button>
            ))}
          </div>
        )}
      </aside>

      {/* Lienzo Principal */}
      <main style={{ flexGrow: 1, background: '#050505', position: 'relative' }}>
        {activeTab === 'flujos' ? (
          <ReactFlow nodes={nodes} />
        ) : (
          <div style={{ padding: '40px' }}><h2>Sección {activeTab} en construcción</h2></div>
        )}
      </main>
    </div>
  );
}

const btnStyle = { background: '#27272a', color: 'white', border: 'none', padding: '12px', borderRadius: '6px', cursor: 'pointer', textAlign: 'left' };
const nodeBtn = { display: 'block', width: '100%', background: '#333', color: 'white', border: 'none', padding: '8px', margin: '5px 0', borderRadius: '4px', cursor: 'pointer' };
