'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, applyEdgeChanges, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';

export default function Home() {
  const [nodes, setNodes] = useState([
    { id: '1', type: 'input', data: { label: 'Mensaje Bienvenida', text: 'Hola, ¿cómo estás?' }, position: { x: 250, y: 50 } },
  ]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onNodeClick = (event, node) => setSelectedNode(node);

  const updateNodeData = (key, value) => {
    setNodes((nds) => nds.map((node) => 
      node.id === selectedNode.id ? { ...node, data: { ...node.data, [key]: value } } : node
    ));
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f0f11', color: 'white' }}>
      {/* 1. Sidebar de Componentes */}
      <aside style={{ width: '250px', borderRight: '1px solid #333', padding: '20px' }}>
        <h3>Bot Builder</h3>
        <button onClick={() => setNodes([...nodes, { id: `${nodes.length + 1}`, data: { label: 'Nuevo Mensaje', text: '' }, position: { x: 50, y: 50 } }])}>
          + Agregar Nodo
        </button>
      </aside>

      {/* 2. El Lienzo */}
      <div style={{ flexGrow: 1 }}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onNodeClick={onNodeClick} onConnect={(p) => setEdges((eds) => addEdge(p, eds))}>
          <Background color="#333" />
          <Controls />
        </ReactFlow>
      </div>

      {/* 3. Panel de Configuración (Donde configuras el bot) */}
      {selectedNode && (
        <div style={{ width: '300px', background: '#1c1c1f', padding: '20px', borderLeft: '1px solid #333' }}>
          <h3>Configurar Nodo</h3>
          <label>Mensaje del Bot:</label>
          <textarea 
            value={selectedNode.data.text} 
            onChange={(e) => updateNodeData('text', e.target.value)}
            style={{ width: '100%', height: '100px', background: '#2d2d31', color: 'white', marginTop: '10px' }}
          />
          <button onClick={() => setSelectedNode(null)} style={{ marginTop: '20px' }}>Cerrar</button>
        </div>
      )}
    </div>
  );
}
