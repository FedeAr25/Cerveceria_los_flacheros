'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import BeerForm from '@/components/BeerForm';
import { getCerveza, updateCerveza, deleteCerveza } from '@/lib/api';
import ErrorMessage from '@/components/ErrorMessage';
import Loading from '@/components/Loading';

export default function EditarCervezaPage() {
  const router = useRouter();
  const params = useParams();
  const [cerveza, setCerveza] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cargarCerveza = async () => {
      try {
        const data = await getCerveza(params.id);
        setCerveza(data);
      } catch (err) {
        setError('Error al cargar la cerveza');
      } finally {
        setLoading(false);
      }
    };
    if (params.id) cargarCerveza();
  }, [params.id]);

  const handleSubmit = async (data) => {
    setLoading(true);
    setError('');
    try {
      await updateCerveza(params.id, data);
      router.push('/cervezas');
    } catch (err) {
      setError(err.message || 'Error al actualizar');
    } finally {
      setLoading(false);
    }
  };

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

  return (
    <div className='max-w-2xl mx-auto'>
      <h1 className='font-display text-4xl text-antares-gold mb-8'>Editar Cerveza</h1>
      {error && <ErrorMessage message={error} />}
      <div className='bg-antares-surface rounded-lg border border-antares-gold/20 p-8 mb-6'>
        <BeerForm cerveza={cerveza} onSubmit={handleSubmit} onCancel={() => router.push('/cervezas')} />
      </div>
      <button onClick={handleDelete} className='btn-secondary w-full text-red-500 border-red-500 hover:bg-red-500 hover:text-white'>
        Eliminar Cerveza
      </button>
    </div>
  );
}
