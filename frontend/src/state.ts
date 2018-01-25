import * as ReactRouterRedux from 'react-router-redux';
import * as Redux from 'redux';
import { BaseAction } from 'redux-actions';
import * as ReduxOidc from 'redux-oidc';

export interface RootState {
    readonly oidc: ReduxOidc.UserState;
    readonly router: ReactRouterRedux.RouterState;
}

export const rootReducer: (
    (state: RootState, action: BaseAction) => RootState
) = Redux.combineReducers({
    oidc: ReduxOidc.reducer,
    router: ReactRouterRedux.routerReducer,
});
