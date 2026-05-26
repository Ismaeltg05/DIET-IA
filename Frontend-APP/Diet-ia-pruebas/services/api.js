/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { Platform } from 'react-native';
import Constants from 'expo-constants';

const envApiUrl = process.env.EXPO_PUBLIC_API_URL?.trim();

// Expo puede proporcionar la URI de host cuando se ejecuta dentro del cliente.
const hostUri =
	Constants.expoConfig?.hostUri ||
	Constants.manifest2?.extra?.expoClient?.hostUri ||
	'';

const expoHost = hostUri ? hostUri.split(':')[0] : '';
const defaultNativeHost = Platform.OS === 'android' ? '10.0.2.2' : 'localhost';

// URL que se usa cuando no hay configuración explícita.
// Para Android, usa 10.0.2.2 para acceder al host de desarrollo desde el emulador.
const fallbackBaseUrl = `http://${Platform.OS === 'web' ? 'localhost' : expoHost || defaultNativeHost}:3000`;

const ensureAbsoluteUrl = (value) => {
	if (!value) return null;
	const trimmed = value.trim();
	if (!trimmed) return null;
	// Asegura que la URL tenga protocolo para poder parsearla correctamente.
	const withProtocol = /^https?:\/\//i.test(trimmed)
		? trimmed
		: `http://${trimmed.replace(/^\/+/, '')}`;

	try {
		const parsed = new URL(withProtocol);
		return parsed.toString();
	} catch {
		return null;
	}
};

const ensureNodePort = (url) => {
	try {
		const parsed = new URL(url);
		if (!parsed.port) {
			parsed.port = '3000';
		}
		return parsed.origin;
	} catch {
		return fallbackBaseUrl;
	}
};

const resolveApiUrl = () => {
	if (envApiUrl) {
		const absoluteEnvUrl = ensureAbsoluteUrl(envApiUrl);

		if (!absoluteEnvUrl) {
			return fallbackBaseUrl;
		}

		const sanitizedEnvUrl = ensureNodePort(absoluteEnvUrl);

		// En native, reemplaza localhost por la IP adecuada del emulador si es necesario.
		if (Platform.OS !== 'web' && sanitizedEnvUrl.includes('localhost')) {
			return ensureNodePort(sanitizedEnvUrl.replace('localhost', expoHost || defaultNativeHost));
		}

		return sanitizedEnvUrl;
	}

	return fallbackBaseUrl;
};

const API_URL = resolveApiUrl();

export const buildApiUrl = (path = '') => {
	const normalizedBaseUrl = ensureNodePort(API_URL);
	if (!path) return normalizedBaseUrl;
	const normalizedPath = path.startsWith('/') ? path : `/${path}`;
	return `${normalizedBaseUrl}${normalizedPath}`;
};

// Exporta la URL base calculada o la construye con una ruta relativa.
export default API_URL;