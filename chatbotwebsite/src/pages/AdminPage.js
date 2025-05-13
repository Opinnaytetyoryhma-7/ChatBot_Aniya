import React, { useState, useEffect } from 'react';

function AdminPage() {
  const [tickets, setTickets] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const secretKey = "your-very-secret-key";  // Could also be prompted from user input

    fetch(`http://localhost:8000/admin/tickets?key=${secretKey}`)
      .then(res => {
        if (!res.ok) {
          throw new Error("Unauthorized");
        }
        return res.json();
      })
      .then(data => setTickets(data))
      .catch(err => setError("Access denied or no tickets found."));
  }, []);

  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Admin Ticket Review</h1>
      <ul>
        {tickets.map((ticket, index) => (
          <li key={index}>
            <strong>{ticket.email}:</strong> {ticket.issue_description}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AdminPage;