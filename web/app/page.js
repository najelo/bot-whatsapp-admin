'use client';
import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, applyNodeChanges, addEdge, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';
import { createClient } from '@supabase/supabase-js';

// Inicializa Supabase
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function Home() {
  const [activeView, setActiveView] = useState('flow-builder');
  const [nodes, setNodes] = useState([{ id: '1', data: { label: 'Inicio', text: '', media: '', delay: '' }, position: { x: 250, y: 50 } }]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const addNode = (type) => {
    const newNode = {
      id: Date.now().toString(),
      data: { label: type, text: '', media: '', delay: '' },
      position: { x: Math.random() * 300, y: Math.random() * 300 },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const updateNodeData = (id, key, value) => {
    setNodes((nds) => nds.map((n) => n.id === id ? { ...n, data: { ...n.data, [key]: value } } : n));
    if (selectedNode) setSelectedNode({ ...selectedNode, data: { ...selectedNode.data, [key]: value } });
  };

  const uploadToSupabase = async (file) => {
    const fileName = `${Date.now()}_${file.name}`;
    const { data, error } = await supabase.storage.from('archivos-bot').upload(fileName, file);
    if (error) { alert("Error al subir: " + error.message); return null; }
    const { data: publicUrl } = supabase.storage.from('archivos-bot').getPublicUrl(fileName);
    return publicUrl.publicUrl;
  };

  const saveFlow = async () => {
    const { error } = await supabase.from('nodos').upsert({ id: 'flow_principal', nodes, edges });
    alert(error ? 'Error al guardar: ' + error.message : '¡Flujo guardado con éxito!');
  };

  const renderView = () => {
    if (activeView !== 'flow-builder') return <div style={{ padding: '40px', color: 'white' }}>Vista: {activeView}</div>;
    
    return (
      <div style={{ display: 'flex', flexGrow: 1 }}>
        <aside style={{ width: '220px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
          <h3>Componentes</h3>
          {['Texto', 'Imagen', 'Esperar', 'Menú'].map(type => (
            <button key={type} style={btnStyle} onClick={() => addNode(type)}>+ Nodo {type}</button>
          ))}
          <button style={{...btnStyle, background: '#4f46e5', marginTop: '20px'}} onClick={saveFlow}>💾 Guardar Flujo</button>
        </aside>

        <div style={{ flexGrow: 1, position: 'relative' }}>
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onConnect={onConnect} onNodeClick={(e, n) => setSelectedNode(n)}>
            <Background color="#333" /> <Controls /> <MiniMap />
          </ReactFlow>
        </div>

        {selectedNode && (
          <div style={{ width: '320px', background: '#1c1c1f', padding: '20px', borderLeft: '1px solid #333', color: 'white', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3>{selectedNode.data.label}</h3>
              <button onClick={() => { setNodes(nds => nds.filter(n => n.id !== selectedNode.id)); setSelectedNode(null); }} style={{ background: '#ff4d4d', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}>🗑️</button>
            </div>
            
            <label>Mensaje:</label>
            <textarea value={selectedNode.data.text} onChange={(e) => updateNodeData(selectedNode.id, 'text', e.target.value)} style={inputStyle} />
            
            {selectedNode.data.label === 'Imagen' && (
              <div style={{marginTop: '10px'}}>
                <label>Subir archivo:</label>
                <input type="file" onChange={async (e) => { const url = await uploadToSupabase(e.target.files[0]); if(url) updateNodeData(selectedNode.id, 'media', url); }} style={{width: '100%'}} />
                <input type="text" placeholder="URL media..." value={selectedNode.data.media || ''} onChange={(e) => updateNodeData(selectedNode.id, 'media', e.target.value)} style={inputStyle} />
              </div>
            )}
            
            {selectedNode.data.label === 'Esperar' && (
              <> <label>Segundos:</label><input type="number" value={selectedNode.data.delay || ''} onChange={(e) => updateNodeData(selectedNode.id, 'delay', e.target.value)} style={inputStyle} /> </>
            )}
            <button onClick={() => setSelectedNode(null)} style={{ width: '100%', padding: '10px', marginTop: '20px' }}>Cerrar</button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0b' }}>
      <aside style={{ width: '240px', background: '#0f0f11', padding: '20px', borderRight: '1px solid #333' }}>
        <h2 style={{ color: 'white', fontSize: '1.2rem', marginBottom: '30px' }}>SendyPRO Admin</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {['flow-builder', 'pagos', 'logs'].map(v => <button key={v} style={navStyle} onClick={() => setActiveView(v)}>{v.toUpperCase()}</button>)}
        </div>
      </aside>
      {renderView()}
    </div>
  );
}

const navStyle = { background: '#2d2d31', color: 'white', border: 'none', padding: '12px', textAlign: 'left', borderRadius: '8px', cursor: 'pointer' };
const btnStyle = { background: '#333', color: 'white', border: 'none', padding: '10px', width: '100%', marginBottom: '10px', borderRadius: '4px', cursor: 'pointer' };
const inputStyle = { width: '100%', background: '#333', color: 'white', border: '1px solid #555', padding: '8px', marginBottom: '10px' };
