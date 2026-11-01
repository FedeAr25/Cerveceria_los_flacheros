"use client";

import { useState } from 'react';

export default function FilterPanel({ onFilter }) {
  const [tipo, setTipo] = useState('');
  const [estilo, setEstilo] = useState('');

  const handleFilter = () => {
    const filters = {};
    if (tipo) filters.tipo = tipo;
    if (estilo) filters.estilo = estilo;
    onFilter(filters);
  };

  return (
    <div className="bg-antares-surface p-4 rounded-lg border border-antares-gold/20 mb-6">
      <h3 className="font-display text-antares-gold mb-3 uppercase tracking-wider text-sm">Filtros</h3>
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[180px]">
          <label className="block text-antares-cream text-xs uppercase tracking-wider mb-1">Tipo</label>
          <select
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            className="antares-input rounded"
          >
            <option value="">Todos los tipos</option>
            <option value="ENVASE">Envase</option>
            <option value="GRIFO">Grifo</option>
          </select>
        </div>
        <div className="flex-1 min-w-[180px]">
          <label className="block text-antares-cream text-xs uppercase tracking-wider mb-1">Estilo</label>
          <select
            value={estilo}
            onChange={(e) => setEstilo(e.target.value)}
            className="antares-input rounded"
          >
            <option value="">Todos los estilos</option>
            <option value="1">IPA</option>
            <option value="2">Stout</option>
            <option value="3">Pilsener</option>
            <option value="4">Wheat</option>
            <option value="5">Amber Ale</option>
          </select>
        </div>
        <button onClick={handleFilter} className="btn-primary">Filtrar</button>
      </div>
    </div>
  );
}
