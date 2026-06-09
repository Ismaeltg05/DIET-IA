import API_URL from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const loginUser = async (email, password) => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Error al iniciar sesión');
  }

  // 🔥 Guardar ID del usuario en AsyncStorage
  if (data.userId) {
    await AsyncStorage.setItem('userId', data.userId);
  }

  return data;
};

export const registerUser = async (name, email, password, phone) => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name,
      email,
      password,
      phone
    })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Error al registrarse');
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