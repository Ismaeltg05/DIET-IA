import { buildApiUrl } from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Intenta convertir la respuesta HTTP en JSON.
// Si la respuesta no es JSON válido, devuelve un objeto vacío.
const parseResponseJson = async (response) => {
  try {
    return await response.json();
  } catch {
    return {};
  }
};

// Devuelve el mensaje de error más relevante disponible en la respuesta del API.
const getApiErrorMessage = (data, fallbackMessage) => {
  return data.error || data.detail || data.message || fallbackMessage;
};

export const loginUser = async (email, password) => {
  const response = await fetch(buildApiUrl('/auth/login'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: email.trim(),
      password
    })
  });

  const data = await parseResponseJson(response);

  if (!response.ok) {
    throw new Error(getApiErrorMessage(data, 'Error al iniciar sesión'));
  }

  // Si el backend devuelve el ID de usuario, lo almacena en AsyncStorage
  // para poder mantener la sesión iniciada entre sesiones de la app.
  if (data.userId) {
    await AsyncStorage.setItem('userId', data.userId);
  }

  return data;
};

export const registerUser = async (name, email, password, phone) => {
  const response = await fetch(buildApiUrl('/auth/register'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: name.trim(),
      email: email.trim(),
      password,
      phone: phone?.trim() || undefined
    })
  });

  const data = await parseResponseJson(response);

  if (!response.ok) {
    throw new Error(getApiErrorMessage(data, 'Error al registrarse'));
  }

  // Devuelve los datos del usuario recién registrado para manejo posterior.
  return data;
};

// Utilidad para obtener el ID de usuario almacenado en AsyncStorage.
export const getUserId = async () => {
  return await AsyncStorage.getItem('userId');
};

// Borra el identificador de usuario guardado localmente para cerrar sesión.
export const logout = async () => {
  await AsyncStorage.removeItem('userId');
};