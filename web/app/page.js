'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, applyEdgeChanges, addEdge, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

export default function Home() {
  const [activeView, setActiveView] = useState('bot-builder');
  const [nodes, setNodes] = useState([
    { id: '1', type: 'input', data: { label: 'Inicio', text: 'Hola, bienvenido' }, position: { x: 250, y: 50 } }
  ]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  // Función para agregar nuevos tipos de nodos al lienzo
  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '' },
      position: { x: Math.random() * 400, y: Math.random() * 400 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const renderContent = () => {
    if (activeView !== 'bot-builder') return <div style={{ padding: '40px' }}>Vista: {activeView}</div>;

    return (
      <div style={{ display: 'flex', flexGrow: 1 }}>
        {/* Panel de Herramientas (Opciones del Lienzo) */}
        <div style={{ width: '200px', background: '#1c1c1f', padding: '15px', borderRight: '1px solid #333' }}>
          <h4>Componentes</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button onClick={() => addNode('Mensaje Texto')} style={toolBtnStyle}>+ Nodo Texto</button>
            <button onClick={() => addNode('Imagen/Archivo')} style={toolBtnStyle}>+ Nodo Imagen</button>
            <button onClick={() => addNode('Menú Opciones')} style={toolBtnStyle}>+ Menú Botones</button>
            <button onClick={() => addNode('Esperar Respuesta')} style={toolBtnStyle}>+ Esperar</button>
          </div>
        </div>

        {/* Lienzo */}
        <div style={{ flexGrow: 1, position: 'relative' }}>
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onConnect={onConnect} onNodeClick={(e, n) => setSelectedNode(n)}>
            <Background color="#333" />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>

        {/* Editor del Nodo seleccionado */}
        {selectedNode && (
          <div style={{ width: '300px', background: '#1c1c1f', padding: '20px', borderLeft: '1px solid #333' }}>
            <h3>Configurar {selectedNode.data.label}</h3>
            <textarea value={selectedNode.data.text} onChange={(e) => setNodes(nodes.map(n => n.id === selectedNode.id ? {...n, data: {...n.data, text: e.target.value}} : n))} style={{ width: '100%', height: '100px', background: '#2d2d31', color: 'white' }} />
            <button onClick={() => setSelectedNode(null)} style={{ marginTop: '20px', width: '100%' }}>Guardar</button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f0f11', color: 'white' }}>
      <aside style={{ width: '200px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
        <h2 style={{ fontSize: '1rem', marginBottom: '20px' }}>SendyPRO Admin</h2>
        <button style={navBtnStyle} onClick={() => setActiveView('bot-builder')}>Lienzo del Bot</button>
        <button style={navBtnStyle} onClick={() => setActiveView('pagos')}>Gestión de Pagos</button>
        <button style={navBtnStyle} onClick={() => setActiveView('logs')}>Logs y Errores</button>
      </aside>
      {renderContent()}
    </div>
  );
}

const toolBtnStyle = { background: '#333', color: 'white', border: 'none', padding: '10px', cursor: 'pointer', borderRadius: '4px' };
const navBtnStyle = { background: 'transparent', border: '1px solid #444', color: 'white', padding: '10px', width: '100%', textAlign: 'left', marginBottom: '10px' };
