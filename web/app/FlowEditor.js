'use client';
import React, { useState } from 'react';

export default function FlowEditor({ node, onUpdate, onClose }) {
  const [settings, setSettings] = useState(node.data);

  return (
    <div style={{ padding: '20px', background: '#111', color: 'white' }}>
      <h3>Configurar: {node.data.label}</h3>
      
      {/* Mensaje */}
      <label>Texto del Bot:</label>
      <textarea value={settings.content} onChange={(e) => setSettings({...settings, content: e.target.value})} />

      {/* Retraso */}
      <label>Retraso (segundos):</label>
      <input type="number" value={settings.delay} onChange={(e) => setSettings({...settings, delay: e.target.value})} />

      {/* Verificación de pago */}
      <div style={{ marginTop: '15px' }}>
        <input type="checkbox" checked={settings.isPaymentCheck} onChange={(e) => setSettings({...settings, isPaymentCheck: e.target.checked})} />
        <label> ¿Verificar pago aquí?</label>
      </div>

      <button onClick={() => onUpdate(node.id, settings)}>Guardar Cambios</button>
    </div>
  );
}
