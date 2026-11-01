"use client";

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function LogoutButton() {
  const { logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <button
      onClick={handleLogout}
      className="text-sm uppercase tracking-widest text-antares-gold border border-antares-gold/50 px-4 py-2 hover:bg-antares-gold hover:text-antares-black transition-all"
    >
      Salir
    </button>
  );
}
