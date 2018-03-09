function getEnv(name: string, defaultValue: string = ''): string {
    return process.env[name] || defaultValue;
}

function getBoolEnv(name: string, defaultValue: boolean = false): boolean {
    const value = getEnv(name, (defaultValue) ? '1' : '0').toLowerCase();
    return (['', '0', 'no', 'false', 'off'].indexOf(value) < 0) ? true : false;
}

export const devMode = (getEnv(
    'NODE_ENV', 'development') === 'development');

export const apiUrl: string = getEnv(
    'REACT_APP_API_URL', ((devMode) ? 'http://localhost:8001/api' : '/api'));

const useLocalTunnistamo: boolean = getBoolEnv(
    'REACT_APP_USE_LOCAL_TUNNISTAMO', devMode);

export const tunnistamoUrl: string = getEnv(
    'REACT_APP_TUNNISTAMO_URL', ((useLocalTunnistamo)
                                 ? 'http://localhost:8000'
                                 : 'https://api.hel.fi/sso'));

export const oidcIssuer: string = getEnv(
    'REACT_APP_OIDC_ISSUER', `${tunnistamoUrl}/openid`);

export const oidcClientId: string = getEnv(
    'REACT_APP_OIDC_CLIENT_ID',
    'https://api.forumvirium.fi/auth/datahubhel-ui');

export const dataHubHelApiId = 'https://api.forumvirium.fi/auth/datahubhel';

export const oidcScopes = `email profile ${dataHubHelApiId}`;
