Muista ladata riippuvuudet terminaalissa:
pip install torch,
pip install stanza,
pip install nltk,
pip install numpy,

intents.json sisältää koulutusmateriaalin. Sitä muokkaamalla Aniya oppii haluttuja tietoja.
training.py pitää ajaa, jotta Aniya saadaan koulutettua.
chat.py ajamalla saadaan Aniyan kanssa keskustelu terminaaliin.


pip install fastapi supabase python-decouple uvicorn

suorita projektin juuressa seuraava komento :
uvicorn backend.main:app --reload

Sovellusta voi testata osoitteessa

http://127.0.0.1:8000/docs