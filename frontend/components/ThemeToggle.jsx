"use client";

import { useTheme } from '@/contexts/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 text-antares-gold hover:text-antares-amber transition-colors text-xl"
      title="Cambiar tema"
    >
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
}
