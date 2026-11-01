"use client";

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useEffect } from 'react';

const cervezaSchema = z.object({
  nombre: z.string().min(3, 'Minimo 3 caracteres'),
  descripcion: z.string().optional(),
  precio: z.number().min(0, 'Precio debe ser >= 0'),
  volumen_ml: z.number().min(100, 'Volumen minimo 100ml'),
  alcohol_pct: z.number().min(0).max(100, 'Entre 0 y 100'),
  stock: z.number().min(0, 'Stock no negativo'),
  tipo: z.enum(['ENVASE', 'GRIFO']),
  estilo: z.number().min(1, 'Selecciona un estilo'),
  activo: z.boolean(),
});

export default function BeerForm({ cerveza = null, onSubmit, onCancel }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(cervezaSchema),
    defaultValues: {
      nombre: '',
      descripcion: '',
      precio: 0,
      volumen_ml: 330,
      alcohol_pct: 5,
      stock: 0,
      tipo: 'ENVASE',
      estilo: 1,
      activo: true,
    },
  });

  useEffect(() => {
    if (cerveza) {
      reset({
        nombre: cerveza.nombre,
        descripcion: cerveza.descripcion || '',
        precio: cerveza.precio,
        volumen_ml: cerveza.volumen_ml,
        alcohol_pct: cerveza.alcohol_pct,
        stock: cerveza.stock,
        tipo: cerveza.tipo,
        estilo: cerveza.estilo,
        activo: cerveza.activo,
      });
    }
  }, [cerveza, reset]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Nombre *</label>
        <input {...register('nombre')} className="antares-input rounded" placeholder="IPA del Flachero" />
        {errors.nombre && <p className="text-red-400 text-xs mt-1">{errors.nombre.message}</p>}
      </div>

      <div>
        <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Descripcion</label>
        <textarea {...register('descripcion')} className="antares-input rounded" rows="3" placeholder="Notas de cata..." />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Precio *</label>
          <input type="number" step="0.01" {...register('precio', { valueAsNumber: true })} className="antares-input rounded" />
          {errors.precio && <p className="text-red-400 text-xs mt-1">{errors.precio.message}</p>}
        </div>
        <div>
          <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Volumen (ml) *</label>
          <input type="number" {...register('volumen_ml', { valueAsNumber: true })} className="antares-input rounded" />
          {errors.volumen_ml && <p className="text-red-400 text-xs mt-1">{errors.volumen_ml.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Alcohol (%) *</label>
          <input type="number" step="0.1" {...register('alcohol_pct', { valueAsNumber: true })} className="antares-input rounded" />
          {errors.alcohol_pct && <p className="text-red-400 text-xs mt-1">{errors.alcohol_pct.message}</p>}
        </div>
        <div>
          <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Stock *</label>
          <input type="number" {...register('stock', { valueAsNumber: true })} className="antares-input rounded" />
          {errors.stock && <p className="text-red-400 text-xs mt-1">{errors.stock.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Tipo *</label>
          <select {...register('tipo')} className="antares-input rounded">
            <option value="ENVASE">Envase</option>
            <option value="GRIFO">Grifo</option>
          </select>
        </div>
        <div>
          <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Estilo *</label>
          <select {...register('estilo', { valueAsNumber: true })} className="antares-input rounded">
            <option value={1}>IPA</option>
            <option value={2}>Stout</option>
            <option value={3}>Pilsener</option>
            <option value={4}>Wheat</option>
            <option value={5}>Amber Ale</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <input type="checkbox" {...register('activo')} id="activo" className="w-4 h-4 accent-amber-600" />
        <label htmlFor="activo" className="text-antares-cream text-sm uppercase tracking-wider">Cerveza activa</label>
      </div>

      <div className="flex gap-4 pt-4">
        <button type="submit" className="btn-primary flex-1">
          {cerveza ? 'Actualizar' : 'Crear'}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className="btn-secondary flex-1">
            Cancelar
          </button>
        )}
      </div>
    </form>
  );
}
