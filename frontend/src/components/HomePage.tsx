import * as OidcClient from 'oidc-client';
import * as React from 'react';
import * as ReactRedux from 'react-redux';

import { RootState } from '../state';
import LoginPage from './LoginPage';
import MainPage from './MainPage';

interface Props {
    user?: OidcClient.User;
}

class HomeView extends React.Component<Props> {
    render() {
        const { user } = this.props;
        const loggedIn = (user && !user.expired);
        return (loggedIn) ? <MainPage/> : <LoginPage/>;
    }
}

const mapStateToProps = (state: RootState): Partial<Props> => ({
    user: state.oidc.user
});

const mapDispatchToProps = null;

const HomePage = ReactRedux.connect(
    mapStateToProps, mapDispatchToProps)(HomeView);

export default HomePage;
