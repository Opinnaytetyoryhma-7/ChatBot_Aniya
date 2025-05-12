import streamlit as st
import requests

st.title("Aniya-demo")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = None
if "description" not in st.session_state:
    st.session_state.description = None

# Näytetään aiemmat viestit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Käyttäjän viestikenttä
if prompt := st.chat_input("Kirjoita viestisi tähän..."):

    # Näytetään viesti ruudulla
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state.conversation_state == "wait_email":
        email = prompt.strip()
        description = st.session_state.description

        # Lähetetään tukipyyntö Supabaseen
        ticket_response = requests.post(
            "http://localhost:8000/ticket",
            json={
                "issue_description": description,
                "email": email,
            },  # Kenttien nimet pitää olla samat kuin BaseModelissa
        )

        bot_reply = ticket_response.json()["response"]

        # Näytetään botin vastaus
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        # Tyhjennetään keskustelun tila ja kuvaus
        st.session_state.conversation_state = None
        st.session_state.description = None

    else:

        response = requests.post(
            "http://localhost:8000/chat",
            json={
                "message": prompt,
                "conversation_state": st.session_state.conversation_state,
            },
        )

        data = response.json()

        # Haetaan keskustelun tila, ja jos sellaista ei löydy, asetetaan se Noneksi
        st.session_state.conversation_state = data.get("conversation_state", None)

        if "issue_description" in data:
            st.session_state.description = data["issue_description"]

        bot_reply = data["response"]

        # Näytetään botin vastaus
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # streamlit run backend/app_test.py