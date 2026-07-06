'use client';
import React, { useState } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function FlowEditor({ node, onUpdate, onClose }) {
  // Estado para la pestaña activa en el editor
  const [activeTab, setActiveTab] = useState('Texto');

  const handleDataChange = (key, value) => {
    onUpdate(node.id, { ...node.data, [key]: value });
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const { data, error } = await supabase.storage.from('bot-media').upload(`${Date.now()}_${file.name}`, file);
    if (!error) {
      const { data: { publicUrl } } = supabase.storage.from('bot-media').getPublicUrl(data.path);
      handleDataChange('mediaUrl', publicUrl);
    }
  };

  return (
    <div style={{ padding: '20px', color: 'white', height: '100%', background: '#18181b' }}>
      <div style={{ display: 'flex', gap: '5px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {['Texto', 'Intervalo', 'Imagen', 'Audio', 'Video', 'Doc'].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={tabButtonStyle(activeTab === tab)}>
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'Texto' && (
        <textarea style={style.input} placeholder="Mensaje..." value={node.data.content || ''} onChange={(e) => handleDataChange('content', e.target.value)} />
      )}

      {activeTab === 'Intervalo' && (
        <input type="number" style={style.input} placeholder="Segundos de espera" value={node.data.delay || ''} onChange={(e) => handleDataChange('delay', e.target.value)} />
      )}

      {['Imagen', 'Audio', 'Video', 'Doc'].includes(activeTab) && (
        <div style={{ padding: '20px', border: '1px dashed #444' }}>
          <input type="file" onChange={handleUpload} />
          {node.data.mediaUrl && <p style={{ color: 'green', fontSize: '12px' }}>✅ Archivo cargado</p>}
        </div>
      )}

      <button onClick={onClose} style={style.saveBtn}>Guardar</button>
    </div>
  );
}

const tabButtonStyle = (active) => ({
  background: active ? '#2563eb' : '#333',
  border: 'none', color: 'white', padding: '8px 12px', cursor: 'pointer', borderRadius: '4px'
});

const style = {
  input: { width: '100%', height: '150px', background: '#0a0a0b', color: 'white', border: '1px solid #444', padding: '10px' },
  saveBtn: { marginTop: '20px', width: '100%', padding: '12px', background: '#2563eb', border: 'none', color: 'white', cursor: 'pointer' }
};
