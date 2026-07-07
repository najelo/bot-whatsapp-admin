'use client';
import React, { useState, useEffect } from 'react';

export default function FlowEditor({ node, onUpdate, onClose }) {
  const [data, setData] = useState({ content: '', delay: 0 });

  useEffect(() => {
    setData(node.data || { content: '', delay: 0 });
  }, [node]);

  return (
    <div className="panel-editor">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h3 style={{ margin: 0 }}>Editar {node.data.label}</h3>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer' }}>✕</button>
      </div>
      
      <label style={{ fontSize: '12px', color: '#71717a' }}>Mensaje</label>
      <textarea value={data.content || ''} onChange={(e) => setData({...data, content: e.target.value})} rows={5} />
      
      <label style={{ display: 'block', marginTop: '15px', fontSize: '12px', color: '#71717a' }}>Tiempo de espera (seg)</label>
      <input type="number" value={data.delay || 0} onChange={(e) => setData({...data, delay: e.target.value})} />
      
      <button onClick={() => onUpdate(node.id, data)} style={{ width: '100%', marginTop: '20px', background: '#3b82f6', color: 'white', border: 'none', padding: '10px', borderRadius: '6px' }}>
        Guardar Cambios
      </button>
    </div>
  );
}
