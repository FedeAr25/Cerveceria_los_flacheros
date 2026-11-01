export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center">
      <h1 className="font-display text-9xl text-antares-gold mb-4">404</h1>
      <p className="text-2xl text-antares-text-muted mb-8">Pagina no encontrada</p>
      <a href="/" className="btn-primary">Volver al inicio</a>
    </div>
  );
}
