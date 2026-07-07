'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { createClient } from '@supabase/supabase-js';
import FlowEditor from './FlowEditor';
import { getNodeStyle } from './NodeStyles';
import 'reactflow/dist/style.css';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    const loadNodes = async () => {
      const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) setNodes(data.nodes || []);
    };
    loadNodes();
  }, []);

  const addNode = (type) => {
    setNodes([...nodes, { 
      id: Date.now().toString(), 
      data: { label: type, content: '', delay: 0 }, 
      position: { x: Math.random() * 200, y: Math.random() * 200 } 
    }]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#09090b', color: '#fff' }}>
      {/* SIDEBAR ÚNICO */}
      <aside style={{ width: '260px', background: '#0f0f12', borderRight: '1px solid #27272a', padding: '20px' }}>
        <h2 style={{ fontSize: '16px' }}>SendyPRO Admin</h2>
        {['Texto', 'Imagen', 'Audio', 'Video', 'PDF'].map(t => (
          <button key={t} onClick={() => addNode(t)} className="sidebar-btn">
            + {t}
          </button>
        ))}
      </aside>

      {/* LIENZO */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow 
          nodes={nodes.map(n => ({ ...n, style: getNodeStyle(n.data.label) }))}
          onNodeClick={(_, n) => setSelectedNode(n)}
        />
      </main>

      {/* EDITOR */}
      {selectedNode && (
        <aside style={{ width: '300px', background: '#0f0f12', borderLeft: '1px solid #27272a' }}>
          <FlowEditor 
            node={selectedNode} 
            onUpdate={(id, data) => setNodes(nodes.map(n => n.id === id ? { ...n, data } : n))}
            onClose={() => setSelectedNode(null)} 
          />
        </aside>
      )}
    </div>
  );
}
