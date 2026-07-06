'use client';
import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function FlowEditor({ node, onUpdate, onClose }) {
  const [data, setData] = useState({ content: '', delay: 0, mediaUrl: '' });

  useEffect(() => {
    if (node) setData(node.data || { content: '', delay: 0, mediaUrl: '' });
  }, [node]);

  const handleChange = (key, value) => {
    setData({ ...data, [key]: value });
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const { data: uploadData } = await supabase.storage.from('bot-media').upload(`${Date.now()}_${file.name}`, file);
    const { data: { publicUrl } } = supabase.storage.from('bot-media').getPublicUrl(uploadData.path);
    handleChange('mediaUrl', publicUrl);
  };

  return (
    <div style={{ padding: '20px', background: '#111', color: 'white', height: '100%' }}>
      <h3>Editar: {node?.data?.label}</h3>
      <textarea 
        placeholder="Escribe tu mensaje..."
        value={data.content}
        onChange={(e) => handleChange('content', e.target.value)}
        style={{ width: '100%', height: '100px', background: '#222', color: 'white' }}
      />
      <input 
        type="number" 
        placeholder="Segundos de espera"
        value={data.delay}
        onChange={(e) => handleChange('delay', e.target.value)}
        style={{ width: '100%', margin: '10px 0' }}
      />
      <input type="file" onChange={handleUpload} />
      <button onClick={() => { onUpdate(node.id, data); onClose(); }} style={{ width: '100%', marginTop: '20px', background: '#2563eb' }}>Guardar</button>
    </div>
  );
}
