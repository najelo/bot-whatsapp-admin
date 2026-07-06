'use client';
import React, { useState, useEffect } from 'react';

export default function FlowEditor({ node, onUpdate, onClose }) {
  const [content, setContent] = useState('');

  // Sincroniza el editor con el nodo seleccionado
  useEffect(() => {
    setContent(node?.data?.content || '');
  }, [node]);

  const handleSave = () => {
    onUpdate(node.id, { ...node.data, content });
    onClose();
  };

  return (
    <div style={{ padding: '20px', borderLeft: '1px solid #333', height: '100%', background: '#111', color: 'white' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>Editar: {node?.data?.label}</h3>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}>✕</button>
      </div>
      
      <p>Contenido del mensaje:</p>
      <textarea 
        value={content}
        onChange={(e) => setContent(e.target.value)}
        style={{ width: '100%', height: '150px', background: '#222', color: '#fff', padding: '10px', border: '1px solid #444' }} 
      />
      
      <button onClick={handleSave} style={{ width: '100%', marginTop: '20px', padding: '10px', background: '#2563eb', border: 'none', color: 'white', cursor: 'pointer' }}>
        Guardar cambios
      </button>
    </div>
  );
}
