// web/app/layout.js
export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body style={{ margin: 0, display: 'flex', height: '100vh', background: '#0a0a0b', color: 'white' }}>
        {/* Menú de navegación global */}
        <aside style={{ width: '250px', background: '#1c1c1f', padding: '20px', borderRight: '1px solid #333' }}>
          <h2>SendyPRO Admin</h2>
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button style={navBtn}>🚀 Flujos (Lienzo)</button>
            <button style={navBtn}>💳 Gestión de Pagos</button>
            <button style={navBtn}>📜 Logs y Errores</button>
          </nav>
        </aside>
        <main style={{ flexGrow: 1 }}>{children}</main>
      </body>
    </html>
  );
}

const navBtn = { background: '#333', color: 'white', border: 'none', padding: '12px', textAlign: 'left', cursor: 'pointer', borderRadius: '5px' };
