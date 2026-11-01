'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import BeerForm from '@/components/BeerForm';
import { createCerveza } from '@/lib/api';
import ErrorMessage from '@/components/ErrorMessage';

export default function NuevaCervezaPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data) => {
    setLoading(true);
    setError('');
    try {
      await createCerveza(data);
      router.push('/cervezas');
    } catch (err) {
      setError(err.message || 'Error al crear la cerveza');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='max-w-2xl mx-auto'>
      <h1 className='font-display text-4xl text-antares-gold mb-8'>Nueva Cerveza</h1>
      {error && <ErrorMessage message={error} />}
      <div className='bg-antares-surface rounded-lg border border-antares-gold/20 p-8'>
        <BeerForm onSubmit={handleSubmit} onCancel={() => router.push('/cervezas')} />
      </div>
    </div>
  );
}
