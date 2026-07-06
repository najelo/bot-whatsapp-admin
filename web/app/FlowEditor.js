'use client';
import React from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

export default function FlowEditor({ node, onUpdate, onClose }) {
  const contents = node.data.contents || [];

  const addContent = (type) => {
    onUpdate(node.id, { ...node.data, contents: [...contents, { id: Date.now(), type, value: '', delay: 0 }] });
  };

  const updateContent = (id, key, val) => {
    onUpdate(node.id, { ...node.data, contents: contents.map(c => c.id === id ? { ...c, [key]: val } : c) });
  };

  return (
    <div style={{ padding: '20px', background: '#18181b', color: 'white', height: '100%', overflowY: 'auto' }}>
      <h3>Configurar Nodo: {node.data.label}</h3>
      {contents.map((item) => (
        <div key={item.id} style={{ background: '#27272a', padding: '10px', margin: '10px 0', borderRadius: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{item.type}</span>
            <button onClick={() => onUpdate(node.id, { ...node.data, contents: contents.filter(c => c.id !== item.id) })}>❌</button>
          </div>
          {item.type === 'Texto' && <textarea onChange={(e) => updateContent(item.id, 'value', e.target.value)} value={item.value} style={{ width: '100%', background: '#0a0a0b', color: 'white' }} />}
          {['PDF', 'Imagen', 'Audio', 'Video'].includes(item.type) && (
            <input type="file" onChange={async (e) => {
              const file = e.target.files[0];
              const { data } = await supabase.storage.from('bot-media').upload(`${Date.now()}_${file.name}`, file);
              const { data: { publicUrl } } = supabase.storage.from('bot-media').getPublicUrl(data.path);
              updateContent(item.id, 'value', publicUrl);
            }} />
          )}
          <input type="number" placeholder="Segundos de espera" onChange={(e) => updateContent(item.id, 'delay', e.target.value)} value={item.delay} style={{ width: '100%', marginTop: '5px' }} />
        </div>
      ))}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px' }}>
        {['Texto', 'PDF', 'Imagen', 'Audio', 'Video'].map(t => <button key={t} onClick={() => addContent(t)} style={{ background: '#333', color: 'white', border: 'none', padding: '8px' }}>+ {t}</button>)}
      </div>
      <button onClick={onClose} style={{ width: '100%', padding: '10px', background: '#2563eb', marginTop: '20px' }}>Guardar</button>
    </div>
  );
}
