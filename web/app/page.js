'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

// Inicializa Supabase
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '', 
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
);

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => { setIsClient(true); }, []);

  if (!isClient) return null; // Previene el error de "client-side exception"

  return (
    <div style={{ display: 'flex', height: '100vh', color: 'white' }}>
      {/* Menú Lateral Fijo */}
      <aside style={{ width: '250px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
        <h2>SendyPRO Admin</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button style={btnStyle}>🚀 Flujos</button>
          <button style={btnStyle}>💳 Pagos</button>
          <button style={btnStyle}>📜 Logs</button>
        </div>
      </aside>

      {/* Lienzo del Bot */}
      <div style={{ flexGrow: 1, background: '#0a0a0b' }}>
        <ReactFlow nodes={nodes} onNodesChange={() => {}} />
      </div>
    </div>
  );
}

const btnStyle = { background: '#333', color: 'white', padding: '10px', border: 'none', cursor: 'pointer', textAlign: 'left' };
