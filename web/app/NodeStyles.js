// web/app/NodeStyles.js
export const nodeConfig = {
  Texto: { background: '#2563eb', icon: '💬' },
  Imagen: { background: '#8b5cf6', icon: '🖼️' },
  Audio: { background: '#f59e0b', icon: '🎵' },
  Video: { background: '#ef4444', icon: '🎥' },
  PDF: { background: '#10b981', icon: '📄' }
};

export const getNodeStyle = (type) => ({
  background: nodeConfig[type]?.background || '#333',
  color: 'white',
  borderRadius: '8px',
  padding: '10px',
  border: '2px solid #fff',
  display: 'flex',
  alignItems: 'center',
  gap: '8px'
});
