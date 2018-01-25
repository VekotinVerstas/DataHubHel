import * as React from 'react';
import * as ReduxOidc from 'redux-oidc';

class SilentRenewPage extends React.Component {
    render() {
        return <div/>;
    }

    componentDidMount() {
        ReduxOidc.processSilentRenew();
    }
}

export default SilentRenewPage;
