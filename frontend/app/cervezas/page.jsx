"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getCervezas } from '@/lib/api';
import BeerCard from '@/components/BeerCard';
import SearchBar from '@/components/SearchBar';
import FilterPanel from '@/components/FilterPanel';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import { useAuth } from '@/contexts/AuthContext';

export default function CervezasPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [cervezas, setCervezas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({});

  useEffect(() => {
    const fetchCervezas = async () => {
      if (!token) {
        setError('Debes iniciar sesion para ver el catalogo');
        setLoading(false);
        return;
      }
      
      setLoading(true);
      setError('');
      try {
        const data = await getCervezas(filters);
        setCervezas(data.results || []);
      } catch (err) {
        setError('Error al cargar cervezas: ' + (err.message || 'Desconocido'));
      } finally {
        setLoading(false);
      }
    };
    fetchCervezas();
  }, [filters, token]);

  const handleSearch = (search) => {
    setFilters(prev => ({ ...prev, search }));
  };

  const handleFilter = (newFilters) => {
    setFilters(newFilters);
  };

  if (!token) {
    return (
      <div className="text-center py-20">
        <h2 className="font-display text-3xl text-antares-gold mb-4">Acceso Restringido</h2>
        <p className="text-antares-text-muted mb-6">Debes iniciar sesion para acceder al catalogo</p>
        <button onClick={() => router.push('/login')} className="btn-primary">Ir al Login</button>
      </div>
    );
  }

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="font-display text-4xl text-antares-gold">Nuestro Catalogo</h1>
        <button onClick={() => router.push('/cervezas/nueva')} className="btn-primary text-sm">
          + Nueva Cerveza
        </button>
      </div>
      
      <SearchBar value={filters.search || ''} onChange={handleSearch} />
      <FilterPanel onFilter={handleFilter} />
      
      {cervezas.length === 0 ? (
        <div className="text-center py-12 text-antares-text-muted">
          No hay cervezas que coincidan con los filtros
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cervezas.map((cerveza) => (
            <BeerCard key={cerveza.id} cerveza={cerveza} />
          ))}
        </div>
      )}
    </div>
  );
}
