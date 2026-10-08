import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSummarize = async () => {
    const trimmedUrl = url.trim();

    // Clear previous result
    setSummary("");
    setError("");

    // Validate input
    if (!trimmedUrl) {
      setError("Please enter a webpage URL.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/summarize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: trimmedUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to summarize the webpage."
        );
      }

      setSummary(data.summary);
    } catch (err) {
      console.error("Summarization error:", err);

      setError(
        err.message ||
          "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !loading) {
      handleSummarize();
    }
  };

  return (
    <div className="app">
      <div className="container">

        {/* Header */}
        <header className="header">
          <div className="badge">
            AI POWERED
          </div>

          <h1>
            AI Web Scraper
          </h1>

          <p>
            Enter any webpage URL and get a concise
            AI-generated summary.
          </p>
        </header>

        {/* Main card */}
        <main className="card">

          <label htmlFor="url">
            Webpage URL
          </label>

          <div className="input-row">

            <input
              id="url"
              type="url"
              value={url}
              onChange={(event) =>
                setUrl(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="https://example.com"
              disabled={loading}
            />

            <button
              type="button"
              onClick={handleSummarize}
              disabled={loading}
            >
              {loading
                ? "Summarizing..."
                : "Summarize"}
            </button>

          </div>

          {/* Loading */}
          {loading && (
            <div className="loading">
              <div className="spinner"></div>

              <div>
                <strong>
                  Processing webpage...
                </strong>

                <p>
                  Scraping content and generating
                  an AI summary.
                </p>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="error">
              <strong>
                Something went wrong
              </strong>

              <p>
                {error}
              </p>
            </div>
          )}

          {/* Summary */}
          {summary && !loading && (
            <section className="summary">

              <div className="summary-header">
                <h2>
                  AI Summary
                </h2>

                <span>
                  Generated
                </span>
              </div>

              <div className="summary-content">
                {summary}
              </div>

            </section>
          )}

        </main>

        {/* Footer */}
        <footer>
          <span>
            React
          </span>

          <span>•</span>

          <span>
            FastAPI
          </span>

          <span>•</span>

          <span>
            BeautifulSoup
          </span>

          <span>•</span>

          <span>
            Gemini AI
          </span>
        </footer>

      </div>
    </div>
  );
}

export default App;