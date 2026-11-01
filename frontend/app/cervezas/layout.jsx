import Link from 'next/link';

// Layout anidado para la sección de cervezas (R1: layout anidado)
export default function CervezasLayout({ children }) {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-4">Cervezas</h1>
        <nav className="flex gap-4 mb-4">
          <Link href="/cervezas" className="text-amber-600 hover:underline">Listado</Link>
          <Link href="/cervezas/nueva" className="text-amber-600 hover:underline">Nueva Cerveza</Link>
        </nav>
      </div>
      {children}
    </div>
  );
}
