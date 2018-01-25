import * as OidcClient from 'oidc-client';
import * as React from 'react';
import * as ReactRedux from 'react-redux';

import { RootState } from '../state';
import userManager from '../userManager';

interface Props {
    user?: OidcClient.User;
}

class MainView extends React.Component<Props> {
    render() {
        const { user } = this.props;
        const name = user ? user.profile.name : '<unnamed>';
        return (
            <div>
                <h1>Welcome, {name}!</h1>
                <button onClick={this.onLogoutButtonClicked}>Logout</button>
                <h2>User info</h2>
                <pre>
                    {JSON.stringify(user, null, 2)}
                </pre>
            </div>
        );
    }

    onLogoutButtonClicked = (event: React.SyntheticEvent<HTMLElement>) => {
        event.preventDefault();
        userManager.removeUser();
    }
}

const mapStateToProps = (state: RootState): Partial<Props> => ({
    user: state.oidc.user,
});

const mapDispatchToProps = null;

const MainPage = ReactRedux.connect(
    mapStateToProps, mapDispatchToProps)(MainView);

export default MainPage;
