'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';

// Importación dinámica obligatoria
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

export default function Dashboard() {
  const [nodes, setNodes] = useState([
    { id: '1', data: { label: 'Nodo Inicial' }, position: { x: 250, y: 5 } }
  ]);

  const addNode = (type) => {
    console.log("Agregando nodo:", type); // Esto te confirmará en la consola del navegador si el botón funciona
    const newNode = {
      id: Date.now().toString(),
      data: { label: type },
      position: { x: Math.random() * 400, y: 100 },
    };
    setNodes((prev) => [...prev, newNode]);
  };

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', background: '#000' }}>
      {/* Sidebar con botones que LLAMAN a addNode */}
      <div style={{ width: '200px', padding: '20px', background: '#111', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {['Texto', 'Imagen', 'Audio', 'Video', 'PDF'].map(type => (
          <button 
            key={type} 
            onClick={() => addNode(type)} 
            style={{ padding: '10px', cursor: 'pointer' }}
          >
            + Nodo {type}
          </button>
        ))}
      </div>

      {/* Contenedor del Lienzo: Debe tener altura y ancho definidos */}
      <div style={{ flexGrow: 1, height: '100vh' }}>
        <ReactFlow nodes={nodes} />
      </div>
    </div>
  );
}
