import * as ReduxOidc from 'redux-oidc';

import * as config from './config';

// Construct baseUrl from window.location
const location = window.location;
const proto = location.protocol;
const host = location.hostname;
const portSuffix = location.port ? `:${location.port}` : '';
const baseUrl = `${proto}//${host}${portSuffix}`;

const userManagerConfig = {
    authority: config.oidcIssuer,
    client_id: config.oidcClientId,
    redirect_uri: `${baseUrl}/login-callback`,
    response_type: 'id_token token',
    scope: `openid ${config.oidcScopes}`,
    silent_redirect_uri: `${baseUrl}/login-silent-renew`,
    automaticSilentRenew: true,
    filterProtocolClaims: true,
    loadUserInfo: true,
};

const userManager = ReduxOidc.createUserManager(userManagerConfig);

export default userManager;
