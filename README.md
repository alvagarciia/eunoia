# Eunoia

Eunoia is a psychology-inspired AI assistant designed to guide users through thoughtful self-reflection and emotional understanding. It provides a calm, nonjudgmental space to talk about personal concerns, helping users gain insight through conversation.

---

## 🌱 Project Vision

Eunoia (from the Greek word meaning "beautiful thinking") is designed as a minimal, calming environment where users feel safe sharing thoughts or emotions. With roots in therapy-inspired dialogue, it mimics a structured self-exploration process guided by a supportive AI persona called **Noema**.

The app guides users through:

1. Sharing a concern
2. Clarifying questions
3. Identifying underlying patterns
4. Reflecting on emotional insights
5. Summarizing findings (if desired)

It does not replace therapy, but offers a warm digital space for introspection.

---

## ⚙️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python (Flask)
- **LLM**: OpenAI GPT-4o and GPT-3.5-turbo
- **LangChain**: Used for prompt templating and memory
- **Deployment**: [Render](https://render.com)

---

## ✨ Features

- Minimalist, mobile-friendly chat interface
- Assistant responds as **Noema**, a professional and curious guide
- Session-based memory for continuity of thought during chats
- Automatically resets memory on page reload
- Styled interface with relaxing color palette

---

## 🚀 Usage

Once deployed, users can visit the app and begin chatting with Noema. No signup required. Each new page load starts a fresh session.

You can test it locally by running:

```bash
python run.py
```

Then go to `localhost:5000` in your browser.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it with proper attribution.