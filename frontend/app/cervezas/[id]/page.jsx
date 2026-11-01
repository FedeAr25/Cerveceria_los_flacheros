'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getCerveza, deleteCerveza } from '@/lib/api';
import Link from 'next/link';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';

export default function CervezaDetallePage() {
  const params = useParams();
  const router = useRouter();
  const [cerveza, setCerveza] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCerveza = async () => {
      try {
        setLoading(true);
        const data = await getCerveza(params.id);
        setCerveza(data);
      } catch (err) {
        setError('Error al cargar la cerveza');
      } finally {
        setLoading(false);
      }
    };
    if (params.id) fetchCerveza();
  }, [params.id]);

  const handleDelete = async () => {
    if (!confirm('¿Seguro que queres eliminar esta cerveza?')) return;
    try {
      await deleteCerveza(params.id);
      router.push('/cervezas');
    } catch (err) {
      setError('Error al eliminar');
    }
  };

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;
  if (!cerveza) return <div className='text-center py-8 text-antares-text-muted'>Cerveza no encontrada</div>;

  const precioFormateado = '$' + cerveza.precio;
  const estadoColor = cerveza.activo ? 'text-green-400' : 'text-red-400';
  const estadoTexto = cerveza.activo ? 'Activa' : 'Inactiva';

  return (
    <div className='max-w-4xl mx-auto'>
      <div className='bg-antares-surface rounded-lg border border-antares-gold/20 p-8'>
        <h1 className='font-display text-4xl text-antares-gold mb-6'>{cerveza.nombre}</h1>
        
        <div className='grid grid-cols-2 md:grid-cols-3 gap-6 mb-8'>
          <div className='bg-antares-black/50 p-4 rounded border border-antares-gold/10'>
            <div className='text-antares-text-muted text-xs uppercase tracking-wider mb-1'>Precio</div>
            <div className='text-3xl font-bold text-antares-gold'>{precioFormateado}</div>
          </div>
          <div className='bg-antares-black/50 p-4 rounded border border-antares-gold/10'>
            <div className='text-antares-text-muted text-xs uppercase tracking-wider mb-1'>Volumen</div>
            <div className='text-3xl font-bold'>{cerveza.volumen_ml}ml</div>
          </div>
          <div className='bg-antares-black/50 p-4 rounded border border-antares-gold/10'>
            <div className='text-antares-text-muted text-xs uppercase tracking-wider mb-1'>Alcohol</div>
            <div className='text-3xl font-bold'>{cerveza.alcohol_pct}%</div>
          </div>
          <div className='bg-antares-black/50 p-4 rounded border border-antares-gold/10'>
            <div className='text-antares-text-muted text-xs uppercase tracking-wider mb-1'>Stock</div>
            <div className='text-3xl font-bold'>{cerveza.stock}</div>
          </div>
          <div className='bg-antares-black/50 p-4 rounded border border-antares-gold/10'>
            <div className='text-antares-text-muted text-xs uppercase tracking-wider mb-1'>Tipo</div>
            <div className='text-3xl font-bold text-antares-gold'>{cerveza.tipo}</div>
          </div>
          <div className='bg-antares-black/50 p-4 rounded border border-antares-gold/10'>
            <div className='text-antares-text-muted text-xs uppercase tracking-wider mb-1'>Estado</div>
            <div className={'text-3xl font-bold ' + estadoColor}>{estadoTexto}</div>
          </div>
        </div>

        {cerveza.descripcion && (
          <div className='mb-8'>
            <div className='text-antares-text-muted text-xs uppercase tracking-wider mb-2'>Descripcion</div>
            <p className='text-lg text-antares-cream leading-relaxed'>{cerveza.descripcion}</p>
          </div>
        )}

        <div className='gold-divider'></div>

        <div className='flex gap-4'>
          <Link href={'/cervezas/' + params.id + '/editar'} className='btn-primary flex-1 text-center'>
            Editar
          </Link>
          <button onClick={handleDelete} className='btn-secondary flex-1 text-red-500 border-red-500 hover:bg-red-500 hover:text-white'>
            Eliminar
          </button>
          <Link href='/cervezas' className='btn-secondary flex-1 text-center'>
            Volver
          </Link>
        </div>
      </div>
    </div>
  );
}
