'use client';
import React, { useState, useEffect } from 'react';

export default function FlowEditor({ node, onUpdate, onClose }) {
  const [data, setData] = useState({ content: '', delay: 0, checkPayment: false });

  useEffect(() => {
    setData(node.data || { content: '', delay: 0, checkPayment: false });
  }, [node]);

  return (
    <div style={{ padding: '20px', background: '#0f0f12', color: '#fff', height: '100%', borderLeft: '1px solid #333' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h3>{node.data.label}</h3>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer' }}>✕</button>
      </div>

      <label>Mensaje del Bot:</label>
      <textarea value={data.content} onChange={(e) => setData({...data, content: e.target.value})} style={{ width: '100%', height: '80px', background: '#222', color: '#fff' }} />

      <label style={{ display: 'block', marginTop: '15px' }}>Retraso (segundos):</label>
      <input type="number" value={data.delay} onChange={(e) => setData({...data, delay: e.target.value})} style={{ width: '100%', background: '#222', color: '#fff' }} />

      <div style={{ marginTop: '15px' }}>
        <input type="checkbox" checked={data.checkPayment} onChange={(e) => setData({...data, checkPayment: e.target.checked})} />
        <label> ¿Verificar pago aquí?</label>
      </div>

      <button onClick={() => { onUpdate(node.id, data); onClose(); }} style={{ width: '100%', marginTop: '20px', padding: '10px', background: '#2563eb', border: 'none', color: 'white', cursor: 'pointer' }}>
        Guardar Configuración
      </button>
    </div>
  );
}
