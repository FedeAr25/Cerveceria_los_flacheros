// Funciones para consumir la API del backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Funcion auxiliar para hacer requests con autenticacion
async function fetchWithAuth(url, options = {}) {
  // Solo usar localStorage en el navegador (no en servidor)
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = 'Token ' + token;
  }

  const response = await fetch(API_URL + url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = new Error('Error en la API');
    error.status = response.status;
    error.data = await response.json().catch(() => null);
    throw error;
  }

  return response.json();
}

// Cervezas
export const getCervezas = (params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const url = queryString ? '/api/cervezas/?' + queryString : '/api/cervezas/';
  return fetchWithAuth(url);
};

export const getCerveza = (id) => fetchWithAuth('/api/cervezas/' + id + '/');

export const createCerveza = (data) => fetchWithAuth('/api/cervezas/', {
  method: 'POST',
  body: JSON.stringify(data),
});

export const updateCerveza = (id, data) => fetchWithAuth('/api/cervezas/' + id + '/', {
  method: 'PUT',
  body: JSON.stringify(data),
});

export const deleteCerveza = (id) => fetchWithAuth('/api/cervezas/' + id + '/', {
  method: 'DELETE',
});

// Autenticacion
export const login = (username, password) => fetchWithAuth('/api/auth-token/', {
  method: 'POST',
  body: JSON.stringify({ username, password }),
});

// Estilos (para el formulario)
export const getEstilos = () => fetchWithAuth('/api/estilos/');
