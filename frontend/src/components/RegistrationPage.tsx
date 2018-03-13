import * as React from 'react';
import * as ReactRedux from 'react-redux';
import { Dispatch } from 'redux';

import * as actions from '../actions';
import * as api from '../api';
import { RootState } from '../state';
import userManager from '../userManager';

interface Props {
    userData: api.UserData;
    registerUser: (userData?: api.UserData) => void;
}

class RegistrationView extends React.Component<Props> {
    firstNameInput?: HTMLInputElement|null;
    lastNameInput?: HTMLInputElement|null;
    emailInput?: HTMLInputElement|null;

    render() {
        const {firstName, lastName, email} = this.props.userData;
        return (
            <form>
                <h1>Register</h1>

                <div>
                    <label htmlFor="firstName">First name</label>
                    <input
                        id="firstName"
                        name="firstName"
                        defaultValue={firstName}
                        ref={(elem) => { this.firstNameInput = elem; }}
                    />
                </div>
                <div>
                    <label htmlFor="lastName">Last name</label>
                    <input
                        id="lastName"
                        name="lastName"
                        defaultValue={lastName}
                        ref={(elem) => { this.lastNameInput = elem; }}
                    />
                </div>
                <div>
                    <label htmlFor="email">E-mail address</label>
                    <input
                        id="email"
                        name="email"
                        defaultValue={email}
                        ref={(elem) => { this.emailInput = elem; }}
                    />
                </div>

                <button onClick={this.onRegisterButtonClicked}>Register</button>

                <h1>Log out</h1>
                <button onClick={this.onLogoutButtonClicked}>Log out</button>
            </form>
        );
    }

    private onRegisterButtonClicked = (
        event: React.SyntheticEvent<HTMLElement>
    ): void => {
        event.preventDefault();
        const {firstNameInput, lastNameInput, emailInput} = this;
        if (firstNameInput && lastNameInput && emailInput) {
            const userData = {
                firstName: firstNameInput.value,
                lastName: lastNameInput.value,
                email: emailInput.value,
            };
            this.props.registerUser(userData);
        }
    }

    private onLogoutButtonClicked = (
        event: React.SyntheticEvent<HTMLElement>
    ): void => {
        event.preventDefault();
        userManager.removeUser();
    }
}

const mapStateToProps = (state: RootState): Partial<Props> => ({
    userData: getUserDataFromState(state),
});

function getUserDataFromState(state: RootState): api.UserData {
    const user = state.oidc.user;
    const profile = (user) ? user.profile : undefined || {};
    return {
        firstName: profile.given_name,
        lastName: profile.family_name,
        email: profile.email,
    };
}

const mapDispatchToProps = (
    dispatch: Dispatch<RootState>
): Partial<Props> => ({
    registerUser: (userData?: api.UserData) => {
        api.registerMe(userData).then((receivedUserData) => {
            if (receivedUserData) {
                dispatch(actions.setRegisteredUser(receivedUserData));
            }
        });
    },
});

const RegistrationPage = ReactRedux.connect(
    mapStateToProps, mapDispatchToProps)(RegistrationView);

export default RegistrationPage;
