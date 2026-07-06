'use client';
import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import FlowEditor from './FlowEditor';
import 'reactflow/dist/style.css';

// Corregimos el error de "client-side exception" evitando el SSR
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

export default function Dashboard() {
  const [nodes, setNodes] = useState([
    { id: '1', data: { label: 'Inicio', content: '' }, position: { x: 250, y: 50 } }
  ]);
  const [selectedNode, setSelectedNode] = useState(null);

  const addNode = (type) => {
    const newNode = { 
      id: Date.now().toString(), 
      data: { label: type, content: '' }, 
      position: { x: Math.random() * 400, y: Math.random() * 400 } 
    };
    setNodes([...nodes, newNode]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#050505' }}>
      {/* Sidebar de Menú */}
      <aside style={{ width: '260px', background: '#111', color: '#fff', padding: '20px', borderRight: '1px solid #333' }}>
        <h2>SendyPRO Admin</h2>
        <nav>
          <div style={{ margin: '20px 0' }}>🚀 Flujos</div>
          <div style={{ margin: '20px 0' }}>💳 Pagos</div>
          <div style={{ margin: '20px 0' }}>📜 Logs</div>
        </nav>
        <div style={{ marginTop: '40px' }}>
          <h4>AGREGAR NODO</h4>
          {['Texto', 'Imagen', 'Menú', 'Espera'].map(item => (
            <button key={item} onClick={() => addNode(item)} style={{ display: 'block', width: '100%', margin: '10px 0', padding: '10px', background: '#222', color: 'white', border: 'none', cursor: 'pointer' }}>
              + Nodo {item}
            </button>
          ))}
        </div>
      </aside>

      {/* Área del Lienzo */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow 
          nodes={nodes} 
          onNodeClick={(_, node) => setSelectedNode(node)} 
        />
      </main>

      {/* Editor Lateral */}
      {selectedNode && (
        <aside style={{ width: '320px', zIndex: 10 }}>
          <FlowEditor 
            node={selectedNode} 
            onUpdate={(id, newData) => {
              setNodes(nodes.map(n => n.id === id ? { ...n, data: newData } : n));
            }}
            onClose={() => setSelectedNode(null)} 
          />
        </aside>
      )}
    </div>
  );
}
