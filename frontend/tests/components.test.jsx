import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import BeerCard from '@/components/BeerCard';
import ErrorMessage from '@/components/ErrorMessage';

// Test 1: BeerCard renderiza correctamente
describe('BeerCard', () => {
  it('muestra el nombre y precio de la cerveza', () => {
    const cerveza = {
      id: 1,
      nombre: 'IPA del Flachero',
      precio: 4500,
      tipo: 'GRIFO',
      activo: true,
      stock: 50,
    };
    render(<BeerCard cerveza={cerveza} />);
    expect(screen.getByText('IPA del Flachero')).toBeInTheDocument();
    expect(screen.getByText('')).toBeInTheDocument();
  });
});

// Test 2: ErrorMessage muestra el mensaje
describe('ErrorMessage', () => {
  it('muestra el mensaje de error', () => {
    render(<ErrorMessage message="Error de prueba" />);
    expect(screen.getByText('Error de prueba')).toBeInTheDocument();
  });
});

// Test 3: Función de formato de precio
describe('formatPrice', () => {
  const formatPrice = (price) => $;
  it('formatea el precio correctamente', () => {
    expect(formatPrice(4500)).toBe('');
    expect(formatPrice(0)).toBe('');
  });
});

// Test 4: Validación de schema Zod
describe('Validación de formulario', () => {
  it('rechaza nombre vacío', () => {
    const { z } = require('zod');
    const schema = z.object({
      nombre: z.string().min(3, 'Mínimo 3 caracteres'),
    });
    const result = schema.safeParse({ nombre: '' });
    expect(result.success).toBe(false);
  });
});
