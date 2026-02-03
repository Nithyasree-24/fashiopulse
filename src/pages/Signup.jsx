import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signup } from '../api';
import './Auth.css';

const Signup = () => {
    const [formData, setFormData] = useState({ name: '', email: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await signup(formData);
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.error || 'Signup failed');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1>Create Account</h1>
                <p>Start your personalized fashion journey</p>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Full Name</label>
                        <input
                            type="text"
                            required
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        />
                    </div>
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
                    <button type="submit" className="auth-btn">Sign Up</button>
                </form>
                <p className="auth-footer">Already have an account? <Link to="/login">Login</Link></p>
            </div>
        </div>
    );
};

export default Signup;
