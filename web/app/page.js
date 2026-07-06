'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, applyEdgeChanges, addEdge, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

export default function Home() {
  const [activeView, setActiveView] = useState('bot-builder');
  const [nodes, setNodes] = useState([{ id: '1', type: 'input', data: { label: 'Inicio', text: 'Hola!' }, position: { x: 250, y: 50 } }]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const renderContent = () => {
    switch (activeView) {
      case 'bot-builder':
        return (
          <div style={{ display: 'flex', flexGrow: 1 }}>
            <div style={{ flexGrow: 1, position: 'relative' }}>
              <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onConnect={onConnect} onNodeClick={(e, n) => setSelectedNode(n)}>
                <Background color="#333" />
                <Controls />
                <MiniMap />
              </ReactFlow>
            </div>
            {selectedNode && (
              <div style={{ width: '300px', background: '#1c1c1f', padding: '20px', borderLeft: '1px solid #333' }}>
                <h3>Configurar Nodo</h3>
                <label>Respuesta:</label>
                <textarea value={selectedNode.data.text} onChange={(e) => setNodes(nodes.map(n => n.id === selectedNode.id ? {...n, data: {...n.data, text: e.target.value}} : n))} style={{ width: '100%', height: '100px', background: '#2d2d31', color: 'white', marginTop: '10px' }} />
                <button onClick={() => setSelectedNode(null)} style={{ marginTop: '20px', width: '100%' }}>Cerrar</button>
              </div>
            )}
          </div>
        );
      case 'pagos':
        return <div style={{ padding: '40px' }}><h1>Gestión de Pagos</h1><p>Conectaremos la API aquí próximamente.</p></div>;
      case 'logs':
        return <div style={{ padding: '40px' }}><h1>Logs del Sistema</h1><p>Historial de actividad de tu bot.</p></div>;
      default:
        return <div>Selecciona una opción</div>;
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f0f11', color: 'white', fontFamily: 'sans-serif' }}>
      <aside style={{ width: '250px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
        <h2 style={{ marginBottom: '30px', fontSize: '1.2rem' }}>SendyPRO Admin</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button style={navBtnStyle} onClick={() => setActiveView('bot-builder')}>Lienzo del Bot</button>
          <button style={navBtnStyle} onClick={() => setActiveView('pagos')}>Gestión de Pagos</button>
          <button style={navBtnStyle} onClick={() => setActiveView('logs')}>Logs y Errores</button>
        </nav>
      </aside>
      {renderContent()}
    </div>
  );
}

const navBtnStyle = {
  background: 'transparent',
  border: '1px solid #444',
  color: 'white',
  padding: '10px',
  textAlign: 'left',
  cursor: 'pointer',
  borderRadius: '4px'
};
