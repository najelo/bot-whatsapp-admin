import React, { useState } from 'react';

export default function FlowEditor({ node, onClose }) {
  const [text, setText] = useState(node.data.text || '');

  return (
    <div style={{ padding: '20px' }}>
      <h3>Editar: {node.data.label}</h3>
      <label>Mensaje del Bot:</label>
      <textarea 
        value={text} 
        onChange={(e) => setText(e.target.value)}
        style={{ width: '100%', height: '100px', background: '#333', color: 'white' }}
      />
      <button onClick={onClose} style={{ marginTop: '10px', width: '100%' }}>Guardar y Cerrar</button>
    </div>
  );
}
