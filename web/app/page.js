'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, addEdge, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

export default function Home() {
  const [activeView, setActiveView] = useState('flow-builder');
  const [nodes, setNodes] = useState([{ id: '1', data: { label: 'Inicio' }, position: { x: 250, y: 50 } }]);
  const [edges, setEdges] = useState([]);

  // Lógica del Lienzo
  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const renderView = () => {
    switch (activeView) {
      case 'flow-builder':
        return (
          <div style={{ flexGrow: 1, position: 'relative', background: '#0a0a0b' }}>
            <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onConnect={onConnect}>
              <Background color="#333" />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </div>
        );
      case 'pagos':
        return <div style={{ padding: '40px', color: 'white' }}><h1>Gestión de Pagos</h1><p>Conectado con pagos_utils.py</p></div>;
      case 'logs':
        return <div style={{ padding: '40px', color: 'white' }}><h1>Logs del Sistema</h1><p>Historial y errores</p></div>;
      default:
        return <div>Seleccione una opción</div>;
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#1c1c1f' }}>
      {/* Sidebar Profesional */}
      <aside style={{ width: '260px', background: '#0f0f11', borderRight: '1px solid #333', display: 'flex', flexDirection: 'column', padding: '20px' }}>
        <h2 style={{ color: 'white', fontSize: '1.2rem', marginBottom: '30px' }}>SendyPRO Admin</h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button style={navStyle} onClick={() => setActiveView('flow-builder')}>🤖 Flujos (Lienzo)</button>
          <button style={navStyle} onClick={() => setActiveView('pagos')}>💳 Gestión de Pagos</button>
          <button style={navStyle} onClick={() => setActiveView('logs')}>📜 Logs y Errores</button>
        </div>
      </aside>

      {/* Área Principal */}
      {renderView()}
    </div>
  );
}

const navStyle = {
  background: '#2d2d31', color: 'white', border: 'none', padding: '12px', textAlign: 'left', borderRadius: '8px', cursor: 'pointer'
};
