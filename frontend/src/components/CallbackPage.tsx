import * as React from 'react';
import * as ReactRedux from 'react-redux';
import * as ReactRouterRedux from 'react-router-redux';
import * as ReduxOidc from 'redux-oidc';

import { RootState } from '../state';
import userManager from '../userManager';

interface Props {
    onSuccess: () => void;
    onError: () => void;
}

class CallbackView extends React.Component<Props> {
    render() {
        return (
            <ReduxOidc.CallbackComponent
                userManager={userManager}
                successCallback={this.successCallback}
                errorCallback={this.errorCallback}
            >
                <div>
                    Redirecting...
                </div>
            </ReduxOidc.CallbackComponent>
        );
    }

    private successCallback = () => {
        this.props.onSuccess();
    }

    private errorCallback = () => {
        this.props.onError();
    }
}

const mapStateToProps = null;

const mapDispatchToProps = (
    dispatch: ReactRedux.Dispatch<RootState>
): Partial<Props> => ({
    onSuccess: () => dispatch(ReactRouterRedux.push('/')),
    onError: () => dispatch(ReactRouterRedux.push('/')),
});

const CallbackPage = ReactRedux.connect(
    mapStateToProps, mapDispatchToProps)(CallbackView);

export default CallbackPage;
