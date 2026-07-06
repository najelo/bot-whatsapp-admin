'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import FlowEditor from './FlowEditor';
import { getNodeStyle, nodeConfig } from './NodeStyles';
import 'reactflow/dist/style.css';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
      {/* Menú Lateral */}
      <aside style={{ width: '260px', background: '#0f0f12', padding: '20px', borderRight: '1px solid #27272a' }}>
        <h2 style={{ fontSize: '18px' }}>SendyPRO Admin</h2>
        <div className="sidebar-item">🚀 Flujos</div>
        <div className="sidebar-item">💳 Pagos</div>
        <div className="sidebar-item">📜 Logs</div>
        
        <h4 style={{ marginTop: '30px' }}>AGREGAR NODO</h4>
        {Object.keys(nodeConfig).map(t => (
          <button key={t} onClick={() => setNodes([...nodes, { id: Date.now().toString(), data: { label: t }, position: { x: 50, y: 50 } }])} 
                  style={{ width: '100%', marginBottom: '5px', background: '#2563eb', border: 'none', color: 'white' }}>
            + {t}
          </button>
        ))}
      </aside>

      {/* Lienzo */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow nodes={nodes.map(n => ({ ...n, style: getNodeStyle(n.data.label) }))} onNodeClick={(_, n) => setSelectedNode(n)} />
      </main>

      {/* Editor Lateral */}
      {selectedNode && (
        <aside style={{ width: '350px' }} className="panel-editor">
          <FlowEditor node={selectedNode} onUpdate={(id, d) => setNodes(nodes.map(n => n.id === id ? { ...n, data: d } : n))} onClose={() => setSelectedNode(null)} />
        </aside>
      )}
    </div>
  );
}
