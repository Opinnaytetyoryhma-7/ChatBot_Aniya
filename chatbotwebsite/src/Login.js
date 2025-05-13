import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './styles/Login.css';

function Login() {
    
    //Heres a example way to create a user account needs to be improved.
    fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'user@example.com',
          password: 'userpassword',
          fname: 'John',
          lname: 'Doe',
        }),
      })
        .then(response => response.json())
        .then(data => console.log('User registered:', data))
        .catch(error => console.error('Error registering user:', error));

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const validateForm = () => {
        if (!username || !password) {
            setError('Username and password are Required');
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

            setLoading(false);
        

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            navigate('/protected');
        } else {
            const errorData = await response.json();
            setError(errorData.detail || 'Authentication failed!');
        }
    } catch (error) {
        setLoading(false);
        setError('An error occurred. Please try again later.');
    }

    };
    
    return (
        <div className="login-container">
          <form onSubmit={handleSubmit} className="login-form">
            <h2 className="login-title">Login</h2>
    
            <div className="login-field">
              <label>Username:</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="login-input"
              />
            </div>
    
            <div className="login-field">
              <label>Password:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="login-input"
              />
            </div>
            <p>Don't have an account? <a href="/register">Register here</a>
            </p>
    
            <button type="submit" disabled={loading} className="login-button">
              {loading ? 'Logging in...' : 'Login'}
            </button>
    
            {error && <p className="login-error">{error}</p>}
          </form>
        </div>
      );
    }
export default Login;


