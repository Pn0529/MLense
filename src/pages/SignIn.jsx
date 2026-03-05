import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.jpeg';
import { API_BASE_URL } from '../constants';

const SignIn = () => {
    const [mode, setMode] = useState('login'); // 'login' or 'register'
    const toggleMode = () => setMode(prev => prev === 'login' ? 'register' : 'login');
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [isPhoneValid, setIsPhoneValid] = useState(false);
    const navigate = useNavigate();

    const handlePhoneChange = (e) => {
        const val = e.target.value.replace(/[^0-9]/g, '');
        if (val.length <= 10) {
            setPhone(val);
            const phonePattern = /^[6-9]\d{9}$/;
            setIsPhoneValid(phonePattern.test(val));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Strict Validation
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        const phonePattern = /^[6-9]\d{9}$/;

        if (!emailPattern.test(email)) {
            alert('Please enter a valid Email address.');
            return;
        }
        if (!phonePattern.test(phone)) {
            alert('Please enter a valid 10-digit Indian mobile number.');
            return;
        }

        // Prepare payload
        const payload = mode === 'register'
            ? {
                name,
                email,
                phone: '+91' + phone,
            }
            : {
                email,
                phone: '+91' + phone,
            };

        try {
            const response = await fetch(`${API_BASE_URL}/auth/${mode}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const err = await response.json();
                alert(`Auth error: ${err.detail || response.statusText}`);
                return;
            }
            const data = await response.json();
            // Expect JWT token in response e.g., data.access_token
            if (data.access_token) {
                localStorage.setItem('jwt_token', data.access_token);
            }
            // Store user details locally as before
            localStorage.setItem('userName', name);
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userPhone', '+91' + phone);
            localStorage.setItem('isLoggedIn', 'true');
            // Redirect to dashboard
            navigate('/dashboard');
        } catch (err) {
            console.error('Auth request failed:', err);
            alert('Unable to connect to the authentication server. Please ensure the backend is running and you have whitelisted your IP in MongoDB Atlas.');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-logo">
                    <img src={logo} alt="ExamBridge Logo" />
                </div>
                <h2>Welcome to ExamBridge Nexus</h2>
                <p>Sign in to access your dashboard and resources</p>

                <div style={{ marginBottom: '1rem', textAlign: 'center' }}>
                    <button type="button" onClick={toggleMode} className="btn btn-toggle" style={{ background: 'var(--primary-navy)', color: '#fff' }}>
                        Switch to {mode === 'login' ? 'Register' : 'Login'}
                    </button>
                </div>
                <form id="signin-form" className="auth-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="signin-name">Full Name</label>
                        <input
                            type="text"
                            id="signin-name"
                            name="signin-name"
                            className="form-control"
                            placeholder="e.g. SUNKAVALLI CHARAN RAM"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="signin-email">Email Address</label>
                        <input
                            type="email"
                            id="signin-email"
                            name="signin-email"
                            className="form-control"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group" style={{ position: 'relative' }}>
                        <label htmlFor="signin-phone">Phone Number</label>
                        <input
                            type="tel"
                            id="signin-phone"
                            name="signin-phone"
                            className="form-control"
                            placeholder="e.g. 7893140112"
                            maxLength="10"
                            value={phone}
                            onChange={handlePhoneChange}
                            style={{
                                borderColor: isPhoneValid ? 'var(--primary-green)' : '#ddd',
                                boxShadow: isPhoneValid ? '0 0 0 3px rgba(46, 204, 113, 0.2)' : 'none'
                            }}
                            required
                        />
                        {isPhoneValid && (
                            <i id="phone-feedback" className="fa-solid fa-check"
                                style={{ position: 'absolute', right: '15px', top: '40px', color: 'var(--primary-green)', display: 'block' }}></i>
                        )}
                    </div>
                    <button type="submit" className="btn btn-full" style={{ width: '100%', marginTop: '1.5rem' }}>{mode === 'login' ? 'Sign In' : 'Register'}</button>
                </form>
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .auth-container {
                    min-height: calc(100vh - 70px);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, var(--primary-navy) 0%, var(--secondary-navy) 100%);
                    padding: 2rem;
                }
                .auth-card {
                    background: var(--bg-white);
                    border-radius: var(--border-radius);
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                    padding: 3rem;
                    width: 100%;
                    max-width: 450px;
                    text-align: center;
                }
                .auth-logo { margin-bottom: 2rem; display: inline-block; }
                .auth-logo img { height: 60px; width: auto; object-fit: contain; }
                .auth-card h2 { color: var(--primary-navy); margin-bottom: 0.5rem; font-size: 1.8rem; }
                .auth-form .form-group { margin-bottom: 1.2rem; text-align: left; }
                .auth-form label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: var(--secondary-navy); font-size: 0.9rem; }
            `}} />
        </div>
    );
};

export default SignIn;
