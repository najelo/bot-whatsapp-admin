// web/app/FlowEditor.js
import React from 'react';

export default function FlowEditor({ selectedNode, onUpdate }) {
  if (!selectedNode) return <p>Selecciona un nodo para configurar</p>;

  return (
    <div className="config-panel">
      <h3>Configurar {selectedNode.type}</h3>
      
      {/* Ejemplo: Campo condicional según el tipo */}
      {selectedNode.type === 'IMAGEN' && (
        <input 
          type="text" 
          placeholder="URL de la imagen" 
          onChange={(e) => onUpdate({ ...selectedNode, url: e.target.value })}
        />
      )}

      {selectedNode.type === 'ESPERAR' && (
        <input 
          type="number" 
          placeholder="Segundos" 
          onChange={(e) => onUpdate({ ...selectedNode, seconds: e.target.value })}
        />
      )}
      
      {/* Aquí seguirías añadiendo casos para AUDIO, PDF, etc. */}
    </div>
  );
}
