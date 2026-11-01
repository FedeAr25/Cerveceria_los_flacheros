export default function ErrorMessage({ message }) {
  return (
    <div className="bg-red-900/20 border border-red-500/50 text-red-400 px-6 py-4 rounded-lg mb-4 flex items-start gap-3">
      <span className="text-2xl">⚠</span>
      <div>
        <p className="font-bold uppercase tracking-wider text-sm mb-1">Error</p>
        <p>{message || 'Ocurrió un error inesperado'}</p>
      </div>
    </div>
  );
}
