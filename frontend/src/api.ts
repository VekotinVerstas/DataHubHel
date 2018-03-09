import globalAxios, * as Axios from 'axios';
import * as OidcClient from 'oidc-client';

import * as config from './config';

export interface UserData {
    firstName?: string;
    lastName?: string;
    email?: string;
}

export interface RegisteredUserData extends UserData {
    id: string;
    dateJoined: string;
}

let apiTokenInterceptor: number|null = null;

const authAxios: Axios.AxiosInstance = globalAxios.create({
    baseURL: config.tunnistamoUrl,
});

const apiAxios: Axios.AxiosInstance = globalAxios.create({
    baseURL: config.apiUrl,
});

export function handleLogin(user: OidcClient.User): Promise<string> {
    return getApiTokens(user).then((apiTokens) => {
        const apiToken = apiTokens[config.dataHubHelApiId];
        setApiToken(apiToken);
        return apiToken;
    });
}

export function handleLogout(): void {
    clearApiToken();
}

function getApiTokens(user: OidcClient.User) {
    const url = `/api-tokens/?access_token=${user.access_token}`;
    return authAxios.get(url).then((result) => result.data);
}

function setApiToken(apiToken?: string): void {
    if (!apiToken || apiTokenInterceptor != null) {
        clearApiToken();
    }
    if (apiToken) {
        apiTokenInterceptor = apiAxios.interceptors.request.use(
            (request: Axios.AxiosRequestConfig) => ({
                ...request,
                headers: {
                    ...request.headers,
                    'Authorization': `Bearer ${apiToken}`,
                }
            }));
    }
}

function clearApiToken(): void {
    if (apiTokenInterceptor != null) {
        apiAxios.interceptors.request.eject(apiTokenInterceptor);
        apiTokenInterceptor = null;
    }
}

export function apiIndex() {
    return apiAxios.get('/');
}

export function getPersonalData(): Promise<RegisteredUserData|null> {
    return apiAxios.get('/me/').then(
        (result) => convertUserData(result.data)
    ).catch(
        (error) => {
            if (error.response.status === 404) {
                return null;
            }
            throw error;
        }
    );
}

export function registerMe(data?: UserData): Promise<RegisteredUserData|null> {
    const params = {
        first_name: data && data.firstName,
        last_name: data && data.lastName,
        email: data && data.email,
    };
    return apiAxios.post('/me/register/', params).then(
        (result) => convertUserData(result.data)
    ).catch(
        (error) => {
            const {response} = error;
            if (response.status === 400 &&
                'non_field_errors' in response.data) {
                // Already registered
                return null;
            }
            throw error;
        }
    );
}

export function forgetMe(): Promise<boolean> {
    return apiAxios.delete('/me/forget/').then(
        (result) => true
    ).catch(
        (error) => {
            if (error.response.status === 404) {
                return false;
            }
            throw error;
        }
    );
}

interface ApiUserData {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    date_joined: string;
}

function convertUserData(data: ApiUserData): RegisteredUserData {
    return {
        id: data.id,
        firstName: data.first_name,
        lastName: data.last_name,
        email: data.email,
        dateJoined: data.date_joined,
    };
}
