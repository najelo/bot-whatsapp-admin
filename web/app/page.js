'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, addEdge, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

export default function Home() {
  const [activeView, setActiveView] = useState('flow-builder');
  const [nodes, setNodes] = useState([{ id: '1', data: { label: 'Inicio' }, position: { x: 250, y: 50 } }]);
  const [edges, setEdges] = useState([]);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  // ESTA ES LA FUNCIÓN QUE TE FALTABA PARA CREAR NODOS
  const addNode = (label) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: label },
      position: { x: Math.random() * 400, y: Math.random() * 400 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const renderView = () => {
    if (activeView !== 'flow-builder') return <div style={{ padding: '40px', color: 'white' }}>Sección {activeView}</div>;
    
    return (
      <div style={{ display: 'flex', flexGrow: 1 }}>
        {/* PANEL DE COMPONENTES (Lo que faltaba) */}
        <div style={{ width: '220px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
          <h3 style={{ color: 'white', fontSize: '1rem', marginBottom: '15px' }}>Agregar Nodo</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button style={btnStyle} onClick={() => addNode('Texto')}>+ Nodo Texto</button>
            <button style={btnStyle} onClick={() => addNode('Imagen')}>+ Nodo Imagen</button>
            <button style={btnStyle} onClick={() => addNode('Menú')}>+ Nodo Menú</button>
            <button style={btnStyle} onClick={() => addNode('Esperar')}>+ Nodo Espera</button>
          </div>
        </div>
        {/* LIENZO */}
        <div style={{ flexGrow: 1, position: 'relative' }}>
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onConnect={onConnect}>
            <Background color="#333" />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0b' }}>
      <aside style={{ width: '240px', background: '#0f0f11', borderRight: '1px solid #333', padding: '20px' }}>
        <h2 style={{ color: 'white', fontSize: '1.2rem', marginBottom: '30px' }}>SendyPRO Admin</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button style={navStyle} onClick={() => setActiveView('flow-builder')}>🤖 Flujos (Lienzo)</button>
          <button style={navStyle} onClick={() => setActiveView('pagos')}>💳 Gestión de Pagos</button>
          <button style={navStyle} onClick={() => setActiveView('logs')}>📜 Logs y Errores</button>
        </div>
      </aside>
      {renderView()}
    </div>
  );
}

const navStyle = { background: '#2d2d31', color: 'white', border: 'none', padding: '12px', textAlign: 'left', borderRadius: '8px', cursor: 'pointer' };
const btnStyle = { background: '#333', color: 'white', border: 'none', padding: '10px', borderRadius: '5px', cursor: 'pointer' };
