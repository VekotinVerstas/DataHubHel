function getEnv(name: string, defaultValue: string = ''): string {
    return process.env[name] || defaultValue;
}

function getBoolEnv(name: string, defaultValue: boolean = false): boolean {
    const value = getEnv(name, (defaultValue) ? '1' : '0').toLowerCase();
    return (['', '0', 'no', 'false', 'off'].indexOf(value) < 0) ? true : false;
}

export const devMode = (getEnv(
    'NODE_ENV', 'development') === 'development');

const useLocalOidc: boolean = getBoolEnv(
    'REACT_APP_USE_LOCAL_OIDC', devMode);

export const apiUrl: string = getEnv(
    'REACT_APP_API_URL', ((devMode) ? 'http://localhost:8001/api' : '/api'));

export const oidcIssuer: string = getEnv(
    'REACT_APP_OIDC_ISSUER', ((useLocalOidc) ? 'http://localhost:8000/openid' :
                              'https://api.hel.fi/sso/openid'));

export const oidcClientId: string = getEnv(
    'REACT_APP_OIDC_CLIENT_ID', '332114');
