import * as History from 'history';
import * as OidcClient from  'oidc-client';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as ReactRedux from 'react-redux';
import * as ReactRouter from 'react-router';
import * as ReactRouterRedux from 'react-router-redux';
import * as Redux from 'redux';
import * as ReduxLogger from 'redux-logger';
import * as ReduxOidc from 'redux-oidc';

import CallbackPage from './components/CallbackPage';
import HomePage from './components/HomePage';
import SilentRenewPage from './components/SilentRenewPage';
import * as config from './config';
import registerServiceWorker from './registerServiceWorker';
import { rootReducer } from './state';
import userManager from './userManager';
import { initializeUserManager } from './users';

import './index.css';

OidcClient.Log.logger = console;

// Construct store with middlewares and enchancers
const history = History.createBrowserHistory();
const middlewares: Redux.Middleware[] = [
    ReactRouterRedux.routerMiddleware(history),
];
if (config.devMode) {
    middlewares.push(ReduxLogger.createLogger());
}
const composeEnhancers = (
    (config.devMode && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__)
    || Redux.compose);
const storeEnhancer = Redux.applyMiddleware(...middlewares);
const store = Redux.createStore(rootReducer, composeEnhancers(storeEnhancer));

initializeUserManager(store);

ReactDOM.render(
    <ReactRedux.Provider store={store}>
        <ReduxOidc.OidcProvider store={store} userManager={userManager}>
            <ReactRouterRedux.ConnectedRouter history={history}>
                <div>
                    <ReactRouter.Route
                        exact={true}
                        path="/"
                        component={HomePage}
                    />
                    <ReactRouter.Route
                        path="/login-callback"
                        component={CallbackPage}
                    />
                    <ReactRouter.Route
                        path="/login-silent-renew"
                        component={SilentRenewPage}
                    />
                </div>
            </ReactRouterRedux.ConnectedRouter>
        </ReduxOidc.OidcProvider>
    </ReactRedux.Provider>,
    document.getElementById('root') as HTMLElement
);

registerServiceWorker();
