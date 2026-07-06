'use client';
import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, applyEdgeChanges, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';

// Inicializa Supabase (asegúrate de tener estas variables en .env)
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function Home() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  // Cargar datos al iniciar
  useEffect(() => {
    const fetchData = async () => {
      const { data } = await supabase.from('flow_config').select('*').single();
      if (data) {
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
      }
    };
    fetchData();
  }, []);

  // Guardar en Supabase
  const saveToSupabase = async () => {
    const { error } = await supabase.from('flow_config').upsert({ id: 1, nodes, edges });
    if (error) alert("Error al guardar: " + error.message);
    else alert("¡Flujo guardado con éxito!");
  };

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onNodeClick = (event, node) => setSelectedNode(node);

  const updateNodeData = (key, value) => {
    setNodes((nds) => nds.map((n) => 
      n.id === selectedNode.id ? { ...n, data: { ...n.data, [key]: value } } : n
    ));
    setSelectedNode({...selectedNode, data: {...selectedNode.data, [key]: value}});
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f0f11', color: 'white' }}>
      <aside style={{ width: '250px', borderRight: '1px solid #333', padding: '20px' }}>
        <h3>Bot Builder</h3>
        <button onClick={() => setNodes([...nodes, { id: Date.now().toString(), data: { label: 'Nuevo Paso', text: '' }, position: { x: 50, y: 50 } }])} style={{width:'100%', padding:'10px', background:'#333', border:'none', color:'white', borderRadius:'5px'}}>
          + Agregar Paso
        </button>
        <button onClick={saveToSupabase} style={{width:'100%', marginTop:'20px', padding:'10px', background:'#4f46e5', border:'none', color:'white', borderRadius:'5px'}}>
          Guardar Flujo
        </button>
      </aside>

      <div style={{ flexGrow: 1 }}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onNodeClick={onNodeClick} onConnect={(p) => setEdges((eds) => addEdge(p, eds))}>
          <Background color="#333" />
          <Controls />
        </ReactFlow>
      </div>

      {selectedNode && (
        <div style={{ width: '320px', background: '#1c1c1f', padding: '20px', borderLeft: '1px solid #333' }}>
          <h3>Configurar Paso</h3>
          <label>Nombre del Paso:</label>
          <input value={selectedNode.data.label} onChange={(e) => updateNodeData('label', e.target.value)} style={{width:'100%', marginBottom:'10px', background:'#2d2d31', color:'white', border:'none', padding:'5px'}} />
          
          <label>Respuesta del Bot:</label>
          <textarea value={selectedNode.data.text} onChange={(e) => updateNodeData('text', e.target.value)} style={{width:'100%', height:'80px', background:'#2d2d31', color:'white', border:'none', padding:'5px'}} />
          
          <label>Tipo de Input:</label>
          <select onChange={(e) => updateNodeData('type', e.target.value)} style={{width:'100%', background:'#2d2d31', color:'white', padding:'5px'}}>
            <option value="text">Texto</option>
            <option value="image">Imagen</option>
            <option value="menu">Menú de Opciones</option>
          </select>
          
          <button onClick={() => setSelectedNode(null)} style={{ marginTop: '20px', width:'100%' }}>Cerrar</button>
        </div>
      )}
    </div>
  );
}
