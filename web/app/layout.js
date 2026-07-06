// web/app/layout.js
export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body style={{ margin: 0, padding: 0, background: '#0a0a0b', color: 'white' }}>
        {children}
      </body>
    </html>
  );
}
