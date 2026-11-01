"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import { login as apiLogin } from '@/lib/api';

const loginSchema = z.object({
  username: z.string().min(1, 'Usuario requerido'),
  password: z.string().min(1, 'Contraseña requerida'),
});

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    try {
      const response = await apiLogin(data.username, data.password);
      login(response.token, { username: data.username });
      router.push('/cervezas');
    } catch (err) {
      setError('Usuario o contraseña incorrectos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-antares-surface rounded-lg border border-antares-gold/20 p-8">
          <h1 className="font-display text-4xl text-antares-gold text-center mb-2">Bienvenido</h1>
          <p className="text-antares-text-muted text-center mb-8 italic">Ingresá a tu cuenta</p>
          
          {error && (
            <div className="bg-red-900/20 border border-red-500/50 text-red-400 p-3 rounded mb-6 text-sm">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Usuario</label>
              <input
                {...register('username')}
                className="antares-input rounded"
                placeholder="demo"
              />
              {errors.username && <p className="text-red-400 text-xs mt-1">{errors.username.message}</p>}
            </div>
            
            <div>
              <label className="block text-antares-cream text-sm uppercase tracking-wider mb-2">Contraseña</label>
              <input
                type="password"
                {...register('password')}
                className="antares-input rounded"
                placeholder="••••••••"
              />
              {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50"
            >
              {loading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>
          
          <div className="mt-6 text-center text-antares-text-muted text-xs">
            <p>Usuario demo: <span className="text-antares-gold">demo</span></p>
            <p>Contraseña: <span className="text-antares-gold">demo2026</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}
