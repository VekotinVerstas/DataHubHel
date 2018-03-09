import * as ReactRouterRedux from 'react-router-redux';
import * as Redux from 'redux';
import { BaseAction } from 'redux-actions';
import * as ReduxOidc from 'redux-oidc';

import * as actions from './actions';
import { RegisteredUserData } from './api';

export interface RootState {
    readonly oidc: ReduxOidc.UserState;
    readonly router: ReactRouterRedux.RouterState;
    readonly registration: RegistrationState;
}

export interface RegistrationState {
    readonly checked: boolean;
    readonly isRegistered?: boolean;
    readonly userData?: RegisteredUserData;
}

function registrationReducer(
    state: RegistrationState = {checked: false},
    action: BaseAction,
): RegistrationState {
    if (actions.setRegisteredUser.match(action)) {
        return {
            checked: true,
            isRegistered: true,
            userData: action.payload,
        };
    } else if (actions.setUnregisteredUser.match(action)) {
        return {
            checked: true,
            isRegistered: false,
            userData: undefined,
        };
    } else if (actions.clearRegistrationStatus.match(action)) {
        return {
            checked: false,
            isRegistered: undefined,
            userData: undefined,
        };
    }
    return state;
}

export const rootReducer: (
    (state: RootState, action: BaseAction) => RootState
) = Redux.combineReducers({
    oidc: ReduxOidc.reducer,
    router: ReactRouterRedux.routerReducer,
    registration: registrationReducer,
});
