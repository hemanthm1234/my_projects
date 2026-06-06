# 🅰️ℹ️ Gemini Chatbot 🤖

A 🧠 RAG-based project using the **`gemini-2.5-pro`** pretrained LLM to answer questions based on custom documents.

---

## 📁 Folder Structure

-    🛡️ `.env` — Stores the 🔐 Google API Key
-    🐍 `app.py` — Main script that runs the chatbot logic
-    📦 `requirements.txt` — All the 🧩 libraries required
-    🧪 `Test_API_Connection.py` — Tests 🔗 connection to Gemini LLM via API
-    📁 `faiss_index` — Stores the files uploaded during the session _(automatically deleted after the app is closed)_
     -    📄 `docs.json` — Stores the chunked texts
     -    🧠 `embeddings.npy` — Stores the vector embeddings of the text

---

## 🚀 How to use?

Run the following command in the **`RAG`** environment:

```bash
streamlit run .\app.py
```

!['Chatbot Demo'](Chatbot_Demo.png)

## 📊 Gemini API Rate Limits

📘 **`Learn more:`** [Gemini API Rate Limits Documentation](https://ai.google.dev/gemini-api/docs/rate-limits)

## Limitations
It is only good at answering based on the text and not for generating new information.
!['Limitations'](Limitations.png)
