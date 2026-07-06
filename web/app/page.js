'use client';

import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, { 
  addEdge, Background, Controls, MiniMap, 
  applyEdgeChanges, applyNodeChanges, addEdge as applyEdge 
} from 'reactflow';
import 'reactflow/dist/style.css';

// 1. Aquí definirías tu conexión a Supabase (usando tu cliente de Supabase)
// import { createClient } from '@supabase/supabase-js';

export default function Home() {
  const [nodes, setNodes] = useState([
    { id: '1', type: 'input', data: { label: 'Inicio del Bot' }, position: { x: 250, y: 50 } },
  ]);
  const [edges, setEdges] = useState([]);

  // Funciones básicas de React Flow
  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  // 2. Función para GUARDAR los nodos en Supabase
  const saveFlowToDatabase = async () => {
    console.log("Guardando en Supabase...", { nodes, edges });
    // Aquí iría tu lógica: await supabase.from('nodos').upsert(...)
    alert("¡Flujo guardado con éxito!");
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#0f0f11' }}>
      {/* Sidebar de Control */}
      <aside style={{ width: '280px', background: '#1c1c1f', color: 'white', padding: '20px', borderRight: '1px solid #333' }}>
        <h2 style={{ fontSize: '1.2rem', marginBottom: '20px' }}>Panel de Control</h2>
        
        <button 
          onClick={saveFlowToDatabase}
          style={{ width: '100%', padding: '10px', background: '#4f46e5', border: 'none', borderRadius: '6px', color: 'white', cursor: 'pointer', marginBottom: '10px' }}>
          Guardar Flujo
        </button>

        <div style={{ marginTop: '20px', fontSize: '0.9rem', color: '#a1a1aa' }}>
          <p>• Estado: Conectado a Supabase</p>
          <p>• Bot: Activo</p>
        </div>
      </aside>

      {/* Área del Lienzo Pro */}
      <div style={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background color="#333" gap={20} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
