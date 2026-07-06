'use client';
import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('flujos');

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      {/* Sidebar Moderno */}
      <aside style={{ width: '260px', background: '#0f0f12', padding: '20px', borderRight: '1px solid #27272a' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '30px', color: '#fff' }}>SendyPRO Admin</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <TabButton active={activeTab === 'flujos'} onClick={() => setActiveTab('flujos')}>🚀 Flujos (Lienzo)</TabButton>
          <TabButton active={activeTab === 'pagos'} onClick={() => setActiveTab('pagos')}>💳 Gestión de Pagos</TabButton>
          <TabButton active={activeTab === 'logs'} onClick={() => setActiveTab('logs')}>📜 Logs</TabButton>
        </nav>
      </aside>

      {/* Área de Contenido */}
      <main style={{ flexGrow: 1, background: '#050505', position: 'relative' }}>
        {activeTab === 'flujos' && (
          <div style={{ height: '100%' }}>
            <ReactFlow fitView />
          </div>
        )}
        {activeTab !== 'flujos' && (
          <div style={{ padding: '40px' }}><h1>Sección en desarrollo: {activeTab}</h1></div>
        )}
      </main>
    </div>
  );
}

const TabButton = ({ children, active, onClick }) => (
  <button 
    onClick={onClick}
    style={{
      background: active ? '#27272a' : 'transparent',
      color: active ? '#fff' : '#a1a1aa',
      border: 'none', padding: '12px', textAlign: 'left', borderRadius: '8px',
      cursor: 'pointer', transition: '0.3s'
    }}
  >
    {children}
  </button>
);
