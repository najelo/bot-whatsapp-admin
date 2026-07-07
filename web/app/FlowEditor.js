'use client';
import React, { useState, useEffect } from 'react';

export default function FlowEditor({ node, onUpdate, onClose }) {
  const [data, setData] = useState(node.data);

  useEffect(() => { setData(node.data); }, [node]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h3>Editar {node.data.label}</h3>
        <button onClick={onClose} style={{ background: '#333' }}>✕</button>
      </div>
      
      <label>Mensaje</label>
      <textarea value={data.content || ''} onChange={(e) => setData({...data, content: e.target.value})} rows={5} />
      
      <label style={{ display: 'block', marginTop: '15px' }}>Tiempo de espera</label>
      <input type="number" value={data.delay || 0} onChange={(e) => setData({...data, delay: e.target.value})} />
      
      <button onClick={() => onUpdate(node.id, data)} style={{ width: '100%', marginTop: '20px', background: '#16a34a', color: 'white', border: 'none' }}>
        Guardar
      </button>
    </div>
  );
}
