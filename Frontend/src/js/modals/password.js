export function isStrongPassword(password) {
    const minLength = 8;
    if (password.length < minLength) {
        return { isValid: false, message: 'Password must be at least 8 characters long.' };
    }
    if (!/[A-Z]/.test(password)) {
        return { isValid: false, message: 'Password must contain at least one uppercase letter.' };
    }
    if (!/[a-z]/.test(password)) {
        return { isValid: false, message: 'Password must contain at least one lowercase letter.' };
    }
    if (!/\d/.test(password)) {
        return { isValid: false, message: 'Password must contain at least one digit.' };
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        return { isValid: false, message: 'Password must contain at least one special character.' };
    }
    return { isValid: true, message: '' };
}

export function clearPasswordFields() {
    document.getElementById('signUpPassword').value = '';
    document.getElementById('signUpRePassword').value = '';
}