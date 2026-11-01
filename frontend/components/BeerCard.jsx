import Link from 'next/link';

// Server Component
export default function BeerCard({ cerveza }) {
  const tipoClass = cerveza.tipo === 'GRIFO'
    ? 'bg-green-500/20 text-green-400 border border-green-500/50'
    : 'bg-blue-500/20 text-blue-400 border border-blue-500/50';
  const estadoClass = cerveza.activo ? 'text-green-400' : 'text-red-400';
  const estadoText = cerveza.activo ? 'Activa' : 'Inactiva';
  const stockClass = cerveza.stock > 10 ? 'text-antares-cream' : 'text-red-400';
  const precioText = '$' + cerveza.precio;

  return (
    <div className="group bg-antares-surface rounded-lg border border-antares-gold/20 hover:border-antares-gold transition-all duration-300 hover:shadow-2xl overflow-hidden">
      <div className="bg-gradient-to-r from-antares-gold/20 to-antares-amber/20 p-4 border-b border-antares-gold/20">
        <div className="flex justify-between items-center">
          <span className={'px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ' + tipoClass}>
            {cerveza.tipo}
          </span>
          <span className={'text-xs font-bold uppercase tracking-wider px-2 py-1 rounded ' + estadoClass}>
            {estadoText}
          </span>
        </div>
      </div>

      <div className="p-6">
        <h3 className="font-display text-2xl text-antares-cream mb-2 group-hover:text-antares-gold transition-colors">
          {cerveza.nombre}
        </h3>
        <p className="text-antares-text-muted text-sm mb-4 min-h-10">
          {cerveza.descripcion || 'Sin descripcion'}
        </p>

        <div className="space-y-2 mb-4">
          <div className="flex justify-between text-sm">
            <span className="text-antares-text-muted">Volumen:</span>
            <span className="text-antares-cream">{cerveza.volumen_ml}ml</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-antares-text-muted">Alcohol:</span>
            <span className="text-antares-cream">{cerveza.alcohol_pct}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-antares-text-muted">Stock:</span>
            <span className={stockClass}>{cerveza.stock} unid.</span>
          </div>
        </div>

        <div className="gold-divider"></div>

        <div className="flex justify-between items-center">
          <span className="text-3xl font-bold text-antares-gold">{precioText}</span>
          <Link href={'/cervezas/' + cerveza.id} className="btn-secondary text-sm px-4 py-2">
            Ver detalle
          </Link>
        </div>
      </div>
    </div>
  );
}
