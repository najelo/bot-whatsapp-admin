export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body style={{ margin: 0, background: '#0a0a0b', color: 'white', overflow: 'hidden' }}>
        {children}
      </body>
    </html>
  );
}
