import * as React from 'react';
import * as ReactRedux from 'react-redux';

import { RootState } from '../state';
import LoginPage from './LoginPage';
import MainPage from './MainPage';
import RegistrationPage from './RegistrationPage';

interface Props {
    isLoggedIn?: boolean;
    isRegistered?: boolean;
    isRegistrationChecked?: boolean;
}

class HomeView extends React.Component<Props> {
    render() {
        const { isLoggedIn, isRegistered, isRegistrationChecked } = this.props;
        const isLoading = !isRegistrationChecked;
        return (
            (isLoggedIn && isRegistered) ? <MainPage/> :
            (isLoggedIn && isLoading) ? <div/> :
            (isLoggedIn && !isRegistered) ? <RegistrationPage/> :
            <LoginPage/>);
    }
}

const mapStateToProps = (state: RootState): Partial<Props> => ({
    isLoggedIn: (state.oidc.user && !state.oidc.user.expired),
    isRegistered: state.registration.isRegistered,
    isRegistrationChecked: state.registration.checked,
});

const mapDispatchToProps = null;

const HomePage = ReactRedux.connect(
    mapStateToProps, mapDispatchToProps)(HomeView);

export default HomePage;
