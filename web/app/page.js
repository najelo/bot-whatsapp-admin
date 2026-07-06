'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';

// IMPORTANTE: Esto evita el error de "client-side exception"
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

export default function Dashboard() {
  const [nodes, setNodes] = useState([]);
  
  // Aquí definirás tus nodos iniciales
  const onNodesChange = (changes) => setNodes((nds) => applyNodeChanges(changes, nds));

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
      {/* Menú Izquierdo (Estilo SendyPRO) */}
      <aside style={{ width: '260px', background: '#111', color: '#fff', padding: '20px' }}>
        <h2>SendyPRO Admin</h2>
        <nav>
          <div style={{ margin: '20px 0' }}>🚀 Flujos</div>
          <div style={{ margin: '20px 0' }}>💳 Pagos</div>
          <div style={{ margin: '20px 0' }}>📜 Logs</div>
        </nav>
        <hr style={{ borderColor: '#333' }} />
        <div style={{ marginTop: '20px' }}>
          <h4>COMPONENTES</h4>
          {['Texto', 'Imagen', 'Audio', 'Video', 'PDF', 'Esperar'].map(item => (
            <button key={item} style={{ display: 'block', width: '100%', margin: '10px 0', padding: '10px' }}>
              + {item}
            </button>
          ))}
        </div>
      </aside>

      {/* Lienzo Principal */}
      <main style={{ flexGrow: 1, position: 'relative', background: '#050505' }}>
        <ReactFlow nodes={nodes} />
      </main>

      {/* Editor Lateral Derecho */}
      <aside style={{ width: '320px', background: '#111', color: '#fff', padding: '20px', borderLeft: '1px solid #333' }}>
        <h3>Editar: Imagen</h3>
        <p>Mensaje del Bot:</p>
        <textarea style={{ width: '100%', height: '150px', background: '#222', color: '#fff' }} />
        <button style={{ width: '100%', marginTop: '10px' }}>Guardar y Cerrar</button>
      </aside>
    </div>
  );
}
