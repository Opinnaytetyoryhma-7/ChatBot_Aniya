import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './styles/Login.css';

function Login() {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const validateForm = () => {
        if (!username || !password) {
            setError('Username and password are required');
            return false;
        }
        setError('');
        return true;
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!validateForm()) return;
        setLoading(true);

        const formDetails = new URLSearchParams();
        formDetails.append('username', username);
        formDetails.append('password', password);

        try {
            const response = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formDetails,
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                try {
                    const tokenData = JSON.parse(atob(data.access_token.split('.')[1]));
                    if (tokenData.admin) {
                        navigate('/admin');  // Suoraan admin sivulle jos admin token
                    } else {
                        navigate('/');  // Homepagelle navigointi jos on normi käyttäjä
                    }
                } catch {
                    navigate('/');  // Jos token epäonnistuu
                }
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Authentication failed!');
            }
        } catch (error) {
            setError('An error occurred. Please try again later.');
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="login-container">
          <form onSubmit={handleSubmit} className="login-form">
            <h2 className="login-title">Login</h2>
            <div className="login-field">
              <label>Username (Email):</label>
              <input
                type="email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="login-input"
                required
              />
            </div>
            <div className="login-field">
              <label>Password:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="login-input"
                required
              />
            </div>
            <p>Don't have an account? <a href="/register">Register here</a></p>
            <button type="submit" disabled={loading} className="login-button">
              {loading ? 'Logging in...' : 'Login'}
            </button>
            {error && <p className="login-error">{error}</p>}
          </form>
        </div>
    );
}

export default Login;