import { buildApiUrl } from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const parseResponseJson = async (response) => {
  try {
    return await response.json();
  } catch {
    return {};
  }
};

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

  // Guardar ID del usuario para mantener sesión activa.
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

  return data;
};

// 🔹 utilidad extra (muy recomendable)
export const getUserId = async () => {
  return await AsyncStorage.getItem('userId');
};

export const logout = async () => {
  await AsyncStorage.removeItem('userId');
};