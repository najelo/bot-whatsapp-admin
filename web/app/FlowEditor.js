import React from 'react';

export default function FlowEditor({ selectedNode, onUpdate, onClose }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onUpdate(selectedNode.id, { [name]: value });
  };

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h3>Editando: {selectedNode.data.label}</h3>
      
      <label>Texto del mensaje:</label>
      <textarea 
        name="text"
        value={selectedNode.data.text || ''} 
        onChange={handleChange}
        style={{ width: '100%', background: '#333', color: 'white' }} 
      />

      <label>Archivo (URL/Media):</label>
      <input 
        name="media"
        value={selectedNode.data.media || ''}
        onChange={handleChange}
        style={{ width: '100%', background: '#333', color: 'white' }} 
      />

      <button onClick={onClose} style={{ marginTop: '20px', width: '100%' }}>Cerrar</button>
    </div>
  );
}
