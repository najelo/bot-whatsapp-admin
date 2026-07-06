'use client';
import React, { useState } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function FlowEditor({ node, onUpdate, onClose }) {
  const [uploading, setUploading] = useState(false);

  const handleDataChange = (key, value) => {
    onUpdate(node.id, { ...node.data, [key]: value });
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);

    const { data, error } = await supabase.storage.from('bot-media').upload(`${Date.now()}_${file.name}`, file);
    if (error) { alert('Error: ' + error.message); } 
    else {
      const { data: { publicUrl } } = supabase.storage.from('bot-media').getPublicUrl(data.path);
      handleDataChange('mediaUrl', publicUrl);
    }
    setUploading(false);
  };

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h3>Editar: {node.data.label}</h3>
      
      {node.data.label === 'Texto' ? (
        <textarea style={style.input} value={node.data.content || ''} onChange={(e) => handleDataChange('content', e.target.value)} />
      ) : (
        <div style={{ marginTop: '10px' }}>
          <input type="file" onChange={handleUpload} disabled={uploading} />
          {node.data.mediaUrl && <p style={{ fontSize: '10px', color: 'green' }}>✅ Archivo guardado</p>}
        </div>
      )}
      
      <button onClick={onClose} style={style.saveBtn}>Guardar</button>
    </div>
  );
}
// Dentro del render del FlowEditor.js
<div style={{ marginTop: '15px', borderTop: '1px solid #333', paddingTop: '10px' }}>
  <label style={{ fontSize: '12px', color: '#a1a1aa' }}>Segundos de espera antes de enviar:</label>
  <input
    type="number"
    min="0"
    max="60"
    style={{ ...style.input, height: '40px', marginTop: '5px' }}
    placeholder="Ej: 2"
    value={node.data.delay || 0}
    onChange={(e) => handleDataChange('delay', parseInt(e.target.value))}
  />
</div>

const style = {
  input: { width: '100%', height: '100px', background: '#18181b', color: 'white', border: '1px solid #333', padding: '10px' },
  saveBtn: { marginTop: '20px', width: '100%', padding: '10px', background: '#2563eb', border: 'none', color: 'white', cursor: 'pointer' }
};
