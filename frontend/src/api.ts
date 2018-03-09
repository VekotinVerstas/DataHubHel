import globalAxios, * as Axios from 'axios';
import * as OidcClient from 'oidc-client';

import * as config from './config';

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
