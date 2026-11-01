'use client';

export default function Error({ error, reset }) {
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      <h2 className="font-bold mb-2">Error al cargar las cervezas</h2>
      <p>{error.message}</p>
      <button onClick={reset} className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
        Reintentar
      </button>
    </div>
  );
}
