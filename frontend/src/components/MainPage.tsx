import * as OidcClient from 'oidc-client';
import * as React from 'react';
import * as ReactRedux from 'react-redux';

import * as actions from '../actions';
import * as api from '../api';
import { RootState } from '../state';
import userManager from '../userManager';

interface Props {
    user?: OidcClient.User;
    userData?: api.RegisteredUserData;
    updateUserData: (userData: api.RegisteredUserData|null) => void;
}

interface State {
    actionResult?: string;
}

class MainView extends React.Component<Props, State> {
    render() {
        const { user } = this.props;
        const state = this.state;
        const actionResult = state && state.actionResult;
        const userData = this.props.userData;

        const name = (
            (userData && userData.firstName) ? userData.firstName :
            (user && user.profile) ? user.profile.name :
            '<unnamed>');
        return (
            <div>
                <h1>Welcome, {name}!</h1>
            <button onClick={this.onLogoutButtonClicked}>Logout</button>
                <h2>User info received via OIDC</h2>
                <pre>
                    {(user) ? JSON.stringify(user.profile, null, 2) : null}
                </pre>

                {(userData) ? (<>
                    <h2>User info registered to API</h2>

                    <p>
                        Id: {userData.id}<br/>
                        Joined on: {userData.dateJoined}<br/>
                        Name: {userData.firstName} {userData.lastName}<br/>
                        E-mail: {userData.email}<br/>
                    </p>

                    <button onClick={this.loadMe}>Reload my data</button>
                    <button onClick={this.forgetMe}>Forget me</button>
                    {(actionResult) ? <p>Result: {actionResult}</p> : null}
                </>) : null}
            </div>
        );
    }

    onLogoutButtonClicked = (event: React.SyntheticEvent<HTMLElement>) => {
        event.preventDefault();
        userManager.removeUser();
    }

    private loadMe = () => {
        api.getPersonalData().then((userData) => {
            if (userData) {
                this.setState({actionResult: 'Loaded'});
                this.props.updateUserData(userData);
            } else {
                this.setState({actionResult: 'Not registered'});
                this.props.updateUserData(null);
            }
        });
    }

    private forgetMe = () => {
        api.forgetMe().then((forgotten) => {
            const resultText = (forgotten) ? 'Forgotten' : 'Not registered';
            this.setState({actionResult: resultText});
            this.props.updateUserData(null);
        });
    }
}

const mapStateToProps = (state: RootState): Partial<Props> => ({
    user: state.oidc.user,
    userData: state.registration.userData,
});

const mapDispatchToProps = (
    dispatch: ReactRedux.Dispatch<RootState>
): Partial<Props> => ({
    updateUserData: (userData: api.RegisteredUserData|null) => {
        if (userData) {
            dispatch(actions.setRegisteredUser(userData));
        } else {
            dispatch(actions.setUnregisteredUser());
        }
    },
});

const MainPage = ReactRedux.connect(
    mapStateToProps, mapDispatchToProps)(MainView);

export default MainPage;
