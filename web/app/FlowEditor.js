// web/app/FlowEditor.js
import React from 'react';

export default function FlowEditor({ node, onUpdate, onClose }) {
  if (!node) return null;

  const handleDataChange = (key, value) => {
    onUpdate(node.id, { ...node.data, [key]: value });
  };

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>
        Editar: {node.data.label}
      </h3>

      {/* Caso 1: Nodo de Texto */}
      {node.data.label === 'Texto' && (
        <textarea
          style={inputStyle}
          placeholder="Escribe el mensaje..."
          value={node.data.content || ''}
          onChange={(e) => handleDataChange('content', e.target.value)}
        />
      )}

      {/* Caso 2: Nodos Multimedia (Imagen, Audio, Video, PDF) */}
      {['Imagen', 'Audio', 'Video', 'PDF'].includes(node.data.label) && (
        <>
          <label style={{ fontSize: '12px', color: '#a1a1aa' }}>URL del archivo:</label>
          <input
            type="text"
            style={inputStyle}
            placeholder={`Pega aquí la URL de tu ${node.data.label}`}
            value={node.data.mediaUrl || ''}
            onChange={(e) => handleDataChange('mediaUrl', e.target.value)}
          />
          <p style={{ fontSize: '11px', color: '#666', marginTop: '5px' }}>
            * Sube tu archivo a Supabase Storage y pega el enlace público aquí.
          </p>
        </>
      )}

      <button onClick={onClose} style={saveBtn}>Guardar y Cerrar</button>
    </div>
  );
}

const inputStyle = { 
  width: '100%', height: '100px', background: '#18181b', 
  border: '1px solid #333', color: 'white', padding: '10px', marginTop: '10px', borderRadius: '4px' 
};

const saveBtn = { 
  marginTop: '20px', width: '100%', padding: '10px', background: '#2563eb', 
  color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' 
};
