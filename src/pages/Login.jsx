import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../api';
import './Auth.css';

const Login = () => {
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await login(formData);
            const user = response.data.user;
            localStorage.setItem('user', JSON.stringify(user));
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1>Welcome Back</h1>
                <p>Login to your Fashiopulse AI account</p>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            required
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            required
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        />
                    </div>
                    {error && <p className="error-msg">{error}</p>}
                    <button type="submit" className="auth-btn">Login</button>
                </form>
                <div className="auth-footer">
                    <button className="forgot-btn">Forgot Password?</button>
                    <p>Don't have an account? <Link to="/signup">Sign Up</Link></p>
                </div>
            </div>
        </div>
    );
};

export default Login;
