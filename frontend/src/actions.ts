import actionCreatorFactory from 'typescript-fsa';

import { RegisteredUserData } from './api';

const regAction = actionCreatorFactory('registration-');

export const setRegisteredUser = regAction<RegisteredUserData>('set-user');
export const setUnregisteredUser = regAction('set-unregistered');
export const clearRegistrationStatus = regAction('clear');
