// web/app/page.js
'use client';
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';

const ReactFlow = dynamic(() => import('reactflow'), { ssr: false });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL, 
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export default function FlowBuilder() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  // Cargar nodos de la base de datos al iniciar
  useEffect(() => {
    const fetchFlow = async () => {
      const { data, error } = await supabase.from('nodos').select('*').eq('id', 'flow_principal').single();
      if (data) {
        setNodes(data.nodes);
        setEdges(data.edges);
      }
    };
    fetchFlow();
  }, []);

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type },
      position: { x: Math.random() * 400, y: 100 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const saveToDatabase = async () => {
    const { error } = await supabase.from('nodos').upsert({ id: 'flow_principal', nodes, edges });
    alert(error ? 'Error al guardar' : '¡Flujo guardado en Supabase!');
  };

  return (
    <div style={{ height: '100%', display: 'flex' }}>
      {/* Panel de "Agregar Nodo" */}
      <div style={{ width: '200px', padding: '20px', borderRight: '1px solid #333' }}>
        <h3>Agregar Nodo</h3>
        {['Texto', 'Imagen', 'Menú', 'Espera'].map(t => (
          <button key={t} onClick={() => addNode(t)} style={btnStyle}>+ Nodo {t}</button>
        ))}
        <button onClick={saveToDatabase} style={{...btnStyle, background: '#4f46e5', marginTop: '20px'}}>💾 Guardar</button>
      </div>

      {/* Lienzo ReactFlow */}
      <div style={{ flexGrow: 1 }}>
        <ReactFlow nodes={nodes} edges={edges} />
      </div>
    </div>
  );
}

const btnStyle = { background: '#333', color: 'white', border: 'none', padding: '10px', width: '100%', marginBottom: '10px', cursor: 'pointer' };
