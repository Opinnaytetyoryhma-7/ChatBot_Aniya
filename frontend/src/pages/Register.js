import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Login.css';

function Register() {
  const [form, setForm] = useState({
    email: '',
    password: '',
    fname: '',
    lname: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const data = await response.json();
      setLoading(false);

      if (response.ok) {
        navigate('/login');
      } else {
        setError(data.detail || 'Registration failed.');
      }
    } catch (err) {
      setLoading(false);
      setError('Something went wrong. Try again.');
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleRegister} className="login-form">
        <h2 className="login-title">Register</h2>

        <div className="login-field">
          <label>First Name:</label>
          <input
            type="text"
            name="fname"
            value={form.fname}
            onChange={handleChange}
            className="login-input"
          />
        </div>
        <div className="login-field">
          <label>Last Name:</label>
          <input
            type="text"
            name="lname"
            value={form.lname}
            onChange={handleChange}
            className="login-input"
          />
        </div>
        <div className="login-field">
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            className="login-input"
          />
        </div>
        <div className="login-field">
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            className="login-input"
          />
        </div>
        <button type="submit" disabled={loading} className="login-button">
          {loading ? 'Registering...' : 'Register'}
        </button>
        {error && <p className="login-error">{error}</p>}
      </form>
    </div>
  );
}

export default Register;