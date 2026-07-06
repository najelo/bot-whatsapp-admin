export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body style={{ margin: 0, padding: 0, height: '100vh', background: '#0a0a0b' }}>
        {children}
      </body>
    </html>
  );
}
