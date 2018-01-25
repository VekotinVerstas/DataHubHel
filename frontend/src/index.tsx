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
import registerServiceWorker from './registerServiceWorker';
import { rootReducer } from './state';
import userManager from './userManager';

import './index.css';

OidcClient.Log.logger = console;

const history = History.createBrowserHistory();
const routerMiddleware = ReactRouterRedux.routerMiddleware(history);
const loggerMiddleware = ReduxLogger.createLogger();
const store = Redux.createStore(
    rootReducer,
    Redux.applyMiddleware(
        loggerMiddleware,
        routerMiddleware,
    ));

ReduxOidc.loadUser(store, userManager);

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
