"use client";

import { useState } from 'react';

export default function SearchBar({ value, onChange }) {
  const [search, setSearch] = useState(value || '');

  const handleSearch = (e) => {
    e.preventDefault();
    onChange(search);
  };

  return (
    <form onSubmit={handleSearch} className="flex gap-3 mb-6">
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Buscar cervezas..."
        className="antares-input rounded flex-1"
      />
      <button type="submit" className="btn-primary">Buscar</button>
    </form>
  );
}
