import './globals.css'; // Si tienes un archivo CSS, si no, elimina esta línea

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
