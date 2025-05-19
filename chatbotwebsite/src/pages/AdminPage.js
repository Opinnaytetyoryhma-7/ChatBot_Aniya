import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/AdminPage.css'

function AdminPage() {
  const [tickets, setTickets] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [activeTicket, setActiveTicket] = useState(null);
  const [responseText, setResponseText] = useState("");

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/admin/tickets', {
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        });
        
        if (!response.ok) throw new Error("Failed to fetch tickets");
        const data = await response.json();
        setTickets(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchTickets();
  }, []);

  const handleRespond = (ticket) => {
    setActiveTicket(ticket);
    setResponseText(ticket.admin_response || "");
  };

  const handleSubmitResponse = async () => {
    if (!activeTicket || !responseText.trim()) return;
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/admin/tickets/${activeTicket.ticket_id}`, 
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: "closed",
            admin_response: responseText
          })
        }
      );
      
      if (!response.ok) throw new Error("Failed to update ticket");
      
      setTickets(tickets.map(t => 
        t.ticket_id === activeTicket.ticket_id ? {
          ...t,
          status: "closed",
          admin_response: responseText
        } : t
      ));
      setActiveTicket(null);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading tickets...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="admin-container">
      <h1>Admin Ticket Management</h1>
      
      {activeTicket && (
        <div className="ticket-response-modal">
          <h3>Respond to Ticket #{activeTicket.ticket_id}</h3>
          <p>From: {activeTicket.user_email}</p>
          <p>Issue: {activeTicket.issue_description}</p>
          <textarea
            value={responseText}
            onChange={(e) => setResponseText(e.target.value)}
            placeholder="Type your response here..."
            rows={6}
          />
          <div className="modal-actions">
            <button onClick={() => setActiveTicket(null)}>Cancel</button>
            <button onClick={handleSubmitResponse}>Send & Close Ticket</button>
          </div>
        </div>
      )}

      <table className="tickets-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Description</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.ticket_id} className={ticket.status}>
              <td>{ticket.ticket_id}</td>
              <td>{ticket.user_email}</td>
              <td>{ticket.issue_description}</td>
              <td>{ticket.status}</td>
              <td>{ticket.created_at}</td>
              <td>
                {ticket.status === "open" && (
                  <button onClick={() => handleRespond(ticket)}>
                    Respond
                  </button>
                )}
                {ticket.status === "closed" && ticket.admin_response && (
                  <button onClick={() => handleRespond(ticket)}>
                    View Response
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminPage;