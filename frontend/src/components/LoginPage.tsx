import * as React from 'react';

import userManager from '../userManager';

class LoginPage extends React.Component {
    render(): React.ReactNode {
        return (
            <div>
                <h1>Welcome to DataHubHel!</h1>
                <p>Please log in to continue</p>
                <button onClick={this.onLoginButtonClick}>Login</button>
            </div>
        );
    }

    private onLoginButtonClick = (
        event: React.SyntheticEvent<HTMLElement>
    ): void => {
        event.preventDefault();
        userManager.signinRedirect();
    }
}

export default LoginPage;
