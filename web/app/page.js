'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, addEdge, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

export default function Home() {
  const [activeView, setActiveView] = useState('flow-builder');
  const [nodes, setNodes] = useState([{ id: '1', type: 'input', data: { label: 'Inicio', text: 'Hola!' }, position: { x: 250, y: 50 } }]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '', delay: '', media: '', options: '' },
      position: { x: Math.random() * 400, y: Math.random() * 300 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const updateNodeData = (id, key, value) => {
    setNodes((nds) => nds.map((n) => n.id === id ? { ...n, data: { ...n.data, [key]: value } } : n));
    if (selectedNode) setSelectedNode({ ...selectedNode, data: { ...selectedNode.data, [key]: value } });
  };

  const renderView = () => {
    if (activeView !== 'flow-builder') return <div style={{ padding: '40px', color: 'white' }}>Vista de {activeView}</div>;

    return (
      <div style={{ display: 'flex', flexGrow: 1 }}>
        <aside style={{ width: '200px', background: '#1c1c1f', padding: '15px', borderRight: '1px solid #333' }}>
          <h4 style={{ color: 'white' }}>Componentes</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {['Texto', 'Imagen', 'Esperar', 'Menú'].map(type => (
              <button key={type} onClick={() => addNode(type)} style={btnStyle}>+ Nodo {type}</button>
            ))}
          </div>
        </aside>

        <div style={{ flexGrow: 1, position: 'relative' }}>
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onConnect={onConnect} onNodeClick={(e, n) => setSelectedNode(n)}>
            <Background color="#333" />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>

        {selectedNode && (
          <div style={{ width: '300px', background: '#1c1c1f', padding: '20px', borderLeft: '1px solid #333', color: 'white' }}>
            <h3>Configurar {selectedNode.data.label}</h3>
            <label>Mensaje / Contenido:</label>
            <textarea value={selectedNode.data.text} onChange={(e) => updateNodeData(selectedNode.id, 'text', e.target.value)} style={inputStyle} />
            
            {selectedNode.data.label === 'Imagen' && (
              <> <label>URL Imagen:</label><input type="text" onChange={(e) => updateNodeData(selectedNode.id, 'media', e.target.value)} style={inputStyle} /> </>
            )}
            {selectedNode.data.label === 'Esperar' && (
              <> <label>Segundos:</label><input type="number" onChange={(e) => updateNodeData(selectedNode.id, 'delay', e.target.value)} style={inputStyle} /> </>
            )}
            
            <button onClick={() => setSelectedNode(null)} style={{ width: '100%', padding: '10px', background: '#4f46e5', border: 'none', cursor: 'pointer' }}>Cerrar</button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0b' }}>
      <aside style={{ width: '240px', background: '#0f0f11', padding: '20px', borderRight: '1px solid #333' }}>
        <h2 style={{ color: 'white', fontSize: '1.2rem', marginBottom: '30px' }}>SendyPRO Admin</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {['flow-builder', 'pagos', 'logs'].map(view => (
            <button key={view} style={navStyle} onClick={() => setActiveView(view)}>{view.toUpperCase()}</button>
          ))}
        </div>
      </aside>
      {renderView()}
    </div>
  );
}

const navStyle = { background: '#2d2d31', color: 'white', border: 'none', padding: '12px', textAlign: 'left', borderRadius: '8px', cursor: 'pointer' };
const btnStyle = { background: '#333', color: 'white', border: 'none', padding: '8px', borderRadius: '4px', cursor: 'pointer' };
const inputStyle = { width: '100%', background: '#333', color: 'white', border: '1px solid #555', padding: '8px', marginBottom: '10px' };
