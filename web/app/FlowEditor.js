'use client';
import React from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function FlowEditor({ node, onUpdate, onClose }) {
  // Inicializamos contenidos como un arreglo si no existe
  const contents = node.data.contents || [];

  const addContent = (type) => {
    const newContent = { id: Date.now(), type, value: '', delay: 0 };
    onUpdate(node.id, { ...node.data, contents: [...contents, newContent] });
  };

  const removeContent = (id) => {
    onUpdate(node.id, { ...node.data, contents: contents.filter(c => c.id !== id) });
  };

  const updateContent = (id, key, value) => {
    onUpdate(node.id, { 
      ...node.data, 
      contents: contents.map(c => c.id === id ? { ...c, [key]: value } : c) 
    });
  };

  return (
    <div style={{ padding: '20px', color: 'white', background: '#18181b', height: '100%', overflowY: 'auto' }}>
      <h3>Configurar Nodo</h3>
      
      {contents.map((item, index) => (
        <div key={item.id} style={{ background: '#27272a', padding: '10px', margin: '10px 0', borderRadius: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{item.type}</span>
            <button onClick={() => removeContent(item.id)} style={{ color: 'red', border: 'none', background: 'none' }}>❌</button>
          </div>
          
          {item.type === 'Texto' && <textarea onChange={(e) => updateContent(item.id, 'value', e.target.value)} value={item.value} style={inputStyle} />}
          {['PDF', 'Imagen', 'Audio', 'Video'].includes(item.type) && (
            <input type="file" onChange={async (e) => {
              const file = e.target.files[0];
              const { data } = await supabase.storage.from('bot-media').upload(`${Date.now()}_${file.name}`, file);
              const { data: { publicUrl } } = supabase.storage.from('bot-media').getPublicUrl(data.path);
              updateContent(item.id, 'value', publicUrl);
            }} />
          )}
          <input type="number" placeholder="Segundos de espera" onChange={(e) => updateContent(item.id, 'delay', e.target.value)} value={item.delay} style={{...inputStyle, marginTop: '5px'}} />
        </div>
      ))}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px', marginTop: '20px' }}>
        {['Texto', 'PDF', 'Imagen', 'Audio', 'Video'].map(t => (
          <button key={t} onClick={() => addContent(t)} style={btnStyle}>+ {t}</button>
        ))}
      </div>
      
      <button onClick={onClose} style={{...btnStyle, background: '#2563eb', marginTop: '20px'}}>Guardar y Cerrar</button>
    </div>
  );
}

const inputStyle = { width: '100%', background: '#0a0a0b', color: 'white', border: '1px solid #444', padding: '5px' };
const btnStyle = { background: '#333', color: 'white', border: 'none', padding: '8px', cursor: 'pointer' };
