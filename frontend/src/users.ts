import * as OidcClient from  'oidc-client';
import { Dispatch, Store } from 'redux';
import * as ReduxOidc from 'redux-oidc';

import * as api from './api';
import { RootState } from './state';
import userManager from './userManager';

export function initializeUserManager(store: Store<RootState>) {
    userManager.events.addUserLoaded(
        (user) => handleUserLoaded(store.dispatch, user));
    userManager.events.addUserUnloaded(
        () => handleUserUnloaded(store.dispatch));
    ReduxOidc.loadUser(store, userManager).then(
        (user) => handleUserLoaded(store.dispatch, user));
}

function handleUserLoaded(dispatch: Dispatch<RootState>, user?: OidcClient.User) {
    if (!user) {
        handleUserUnloaded(dispatch);
        return;
    }
    api.handleLogin(user);
}

function handleUserUnloaded(dispatch: Dispatch<RootState>) {
    api.handleLogout();
}
