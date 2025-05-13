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
      setMessage("Kiitos palautteestasi!");
      setForm({
        clarity: "",
        ease_of_use: "",
        chatbot_feedback: "",
        contact_form_feedback: "",
      });
    } else {
      setMessage("Palautteen lähettäminen epäonnistui.");
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h2>Palautelomake</h2>
      <form onSubmit={handleSubmit}>
        <label>Kuinka selkeät verkkosivut ovat?</label>
        <textarea name="clarity" value={form.clarity} onChange={handleChange} />

        <label>Oliko helppo löytää haluama tieto sivustolta?</label>
        <textarea name="ease_of_use" value={form.ease_of_use} onChange={handleChange} />

        <label>Antoiko chatbot asiaan liittyviä vastauksia?</label>
        <textarea name="chatbot_feedback" value={form.chatbot_feedback} onChange={handleChange} />

        <label>Saitko täytettyä ja lähetettyä yhteydenottolomakkeen ja oliko sen teko selkeää?</label>
        <textarea name="contact_form_feedback" value={form.contact_form_feedback} onChange={handleChange} />

        <button type="submit">Lähetä palaute</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default ReviewPage;