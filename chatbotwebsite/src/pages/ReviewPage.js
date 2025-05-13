import React, { useState } from 'react';

function ReviewPage() {
  const [form, setForm] = useState({
    clarity: "",
    ease_of_use: "",
    chatbot_feedback: "",
    contact_form_feedback: ""
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://localhost:8000/review", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    });

    if (res.ok) {
      setMessage("Thank you for your feedback!");
      setForm({
        clarity: "",
        ease_of_use: "",
        chatbot_feedback: "",
        contact_form_feedback: "",
      });
    } else {
      setMessage("Sending feedback failed.");
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h2>Feedback form</h2>
      <form onSubmit={handleSubmit}>
        <label>How is the websites outlook?</label>
        <textarea name="clarity" value={form.clarity} onChange={handleChange} />

        <label>Were you able to find what you were looking for in the website?</label>
        <textarea name="ease_of_use" value={form.ease_of_use} onChange={handleChange} />

        <label>Did the chatbot give useful answers matching your input?</label>
        <textarea name="chatbot_feedback" value={form.chatbot_feedback} onChange={handleChange} />

        <label>Did you manage to send an contact request and was it easy to fill out?</label>
        <textarea name="contact_form_feedback" value={form.contact_form_feedback} onChange={handleChange} />

        <button type="submit">Submit</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default ReviewPage;