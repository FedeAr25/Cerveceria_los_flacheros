"use client";

import './globals.css';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import Link from 'next/link';
import { useState } from 'react';
import ThemeToggle from '@/components/ThemeToggle';
import LogoutButton from '@/components/LogoutButton';

function Navbar() {
  const { token } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 bg-antares-black border-b border-antares-gold/20 backdrop-blur-sm bg-opacity-95">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        {/* Logo */}
        <Link href="/" className="font-display text-2xl text-antares-gold tracking-wider hover:text-antares-amber transition-colors">
          LOS FLACHEROS
        </Link>

        {/* Menu desktop */}
        <div className="hidden md:flex items-center gap-8">
          <Link href="/" className="text-sm uppercase tracking-widest hover:text-antares-gold transition-colors">
            Inicio
          </Link>
          {token && (
            <Link href="/cervezas" className="text-sm uppercase tracking-widest hover:text-antares-gold transition-colors">
              Catálogo
            </Link>
          )}
          {token ? (
            <>
              <ThemeToggle />
              <LogoutButton />
            </>
          ) : (
            <Link href="/login" className="text-sm uppercase tracking-widest text-antares-gold border border-antares-gold px-4 py-2 hover:bg-antares-gold hover:text-antares-black transition-all">
              Ingresar
            </Link>
          )}
        </div>

        {/* Menu mobile */}
        <button
          className="md:hidden text-antares-gold text-2xl"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* Menu mobile desplegable */}
      {menuOpen && (
        <div className="md:hidden bg-antares-dark border-t border-antares-gold/20 px-6 py-4 flex flex-col gap-4">
          <Link href="/" className="text-sm uppercase tracking-widest" onClick={() => setMenuOpen(false)}>Inicio</Link>
          {token && (
            <Link href="/cervezas" className="text-sm uppercase tracking-widest" onClick={() => setMenuOpen(false)}>Catálogo</Link>
          )}
          {token ? (
            <>
              <ThemeToggle />
              <LogoutButton />
            </>
          ) : (
            <Link href="/login" className="text-sm uppercase tracking-widest text-antares-gold" onClick={() => setMenuOpen(false)}>Ingresar</Link>
          )}
        </div>
      )}
    </nav>
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body className="min-h-screen">
        <ThemeProvider>
          <AuthProvider>
            <Navbar />
            <main>
              {children}
            </main>
            <footer className="border-t border-antares-gold/20 py-8 text-center text-antares-text-muted text-sm uppercase tracking-widest bg-antares-black">
              © 2026 Cervecería Los Flacheros · Arte en cada trago
            </footer>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
