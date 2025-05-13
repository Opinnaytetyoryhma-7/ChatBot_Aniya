import React, { useState } from 'react';
import '../styles/ChatWidget.css';

function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [conversationState, setConversationState] = useState(null);

    const toggleChat = () => {
        setIsOpen(!isOpen);
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { sender: 'user', text: input };
        setMessages((prev) => [...prev, userMessage]);

        try {
            const res = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    conversation_state: conversationState,
                }),
            });

            const data = await res.json();

            const botMessage = { sender: 'bot', text: data.response };
            setMessages((prev) => [...prev, botMessage]);

            if (data.conversation_state !== undefined) {
                setConversationState(data.conversation_state);
            }
        } catch (error) {
            console.error("Chat error:", error);
            setMessages((prev) => [...prev, { sender: 'bot', text: "Something went wrong." }]);
        }
        setInput('');
    };

    return (
        <div className='chat-widget'>
            {isOpen && (
                <div className='chat-box'>
                    <div className='chat-header'>Chat</div>
                    <div className='chat-messages'>
                        {messages.map((msg, index) => (
                            <div key={index} className={`chat-msg ${msg.sender}`}>
                                {msg.text}
                            </div>
                        ))}
                    </div>
                    <div className='chat-input'>
                        <input
                            type='text'
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder='Type a message...'
                        />
                        <button onClick={handleSend}>Send</button>
                    </div>
                </div>
            )}
            <button className='chat-toggle' onClick={toggleChat}>
                {isOpen ? 'X' : '💬'}
            </button>
        </div>
    );
}

export default ChatWidget;