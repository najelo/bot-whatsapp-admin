'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { createClient } from '@supabase/supabase-js';
import 'reactflow/dist/style.css';

// Carga dinámica obligatoria para evitar el error de "Application error"
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL, 
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);

  // Carga inicial desde Supabase
  useEffect(() => {
    const fetchNodes = async () => {
      const { data } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) setNodes(data.nodes || []);
    };
    fetchNodes();
  }, []);

  // Función para agregar nodos
  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type },
      position: { x: Math.random() * 400, y: Math.random() * 200 },
    };
    setNodes((prev) => [...prev, newNode]);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#09090b' }}>
      {/* SIDEBAR IZQUIERDO: Menú principal */}
      <aside style={{ width: '260px', background: '#111', padding: '20px', borderRight: '1px solid #333', color: 'white' }}>
        <h2>SendyPRO Admin</h2>
        <div style={{ marginTop: '20px' }}>
          <button className="sidebar-btn" onClick={() => console.log('Flujos')}>🚀 Flujos (Lienzo)</button>
          <button className="sidebar-btn" onClick={() => console.log('Pagos')}>💳 Gestión de Pagos</button>
          <button className="sidebar-btn" onClick={() => console.log('Logs')}>📜 Logs y Errores</button>
        </div>

        <h4 style={{ marginTop: '40px', color: '#888' }}>AGREGAR NODO</h4>
        {['Texto', 'Imagen', 'Audio', 'Video', 'PDF'].map(type => (
          <button key={type} className="sidebar-btn" onClick={() => addNode(type)}>
            + Nodo {type}
          </button>
        ))}
      </aside>

      {/* LIENZO CENTRAL */}
      <main style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow nodes={nodes} />
      </main>
    </div>
  );
}
