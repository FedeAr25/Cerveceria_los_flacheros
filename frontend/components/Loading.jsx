export default function Loading() {
  return (
    <div className="flex flex-col justify-center items-center py-20">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-antares-gold/30 rounded-full"></div>
        <div className="absolute top-0 left-0 w-16 h-16 border-4 border-antares-gold border-t-transparent rounded-full animate-spin"></div>
      </div>
      <p className="mt-4 text-antares-gold uppercase tracking-widest text-sm">Cargando...</p>
    </div>
  );
}
