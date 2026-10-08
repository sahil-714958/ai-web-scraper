# AI Web Scraper

A simple full-stack web application that accepts a webpage URL, extracts readable HTML text, and uses Google's Gemini API to generate a short summary.

## Features

- React + Vite frontend
- FastAPI backend
- Basic webpage scraping with Requests + BeautifulSoup
- Gemini AI summarization
- Loading and error states
- REST API with Swagger documentation
- No database required

## Project Structure

```text
ai-web-scraper/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- A Google Gemini API key

Gemini offers a Free tier for eligible models and usage limits. Create an API key in Google AI Studio.

## 1. Run the Backend

Open a terminal in the `backend` directory:

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a file named `.env` inside **backend/**:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_ORIGIN=http://localhost:5173
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

Swagger API docs: `http://localhost:8000/docs`

## 2. Run the Frontend

Open a second terminal in the `frontend` directory:

```bash
cd frontend
npm install
```

Create a file named `.env` inside **frontend/**:

```env
VITE_API_URL=http://localhost:8000
```

Start Vite:

```bash
npm run dev
```

Open the local URL shown by Vite, normally `http://localhost:5173`.

## 3. How It Works

1. The user enters a webpage URL in React.
2. React sends `POST /summarize` to FastAPI.
3. FastAPI fetches the webpage using Requests.
4. BeautifulSoup removes scripts/styles and extracts readable HTML text.
5. The extracted content is sent to Gemini.
6. Gemini returns a concise summary.
7. FastAPI returns the summary as JSON.
8. React displays the result.

## API

### `POST /summarize`

Request:

```json
{
  "url": "https://example.com"
}
```

Response:

```json
{
  "url": "https://example.com",
  "summary": "..."
}
```

## Limitations

This project intentionally performs simple HTML scraping. It does not render JavaScript-heavy pages or bypass bot protection, which is consistent with the assignment requirements.

Never commit `.env` or expose the Gemini API key in frontend code.

## Deployment

Recommended deployment:

- Frontend: Vercel
- Backend: Render
- Add `GEMINI_API_KEY` to the backend deployment environment variables.
- Set the frontend `VITE_API_URL` to the deployed backend URL.
- Set the backend `FRONTEND_ORIGIN` to the deployed frontend URL.
