# Sales Insight Agent

This project is a Sales Insight Agent, a web application that uses a large language model (LLM) to provide contextual, AI-driven responses, charts, and metrics based on natural language queries about sales data.

## 🚀 Getting Started

Follow these steps to set up and run the application locally.

### 1. Project Structure

The project is organized as follows:

```
sales-insight-agent/
│
├── app.py
├── llm_agent.py
├── utils.py
├── sales_api.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── upsales.json
│
├── .env.example
├── requirements.txt
├── README.md
└── reflection.md
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

The required dependencies are listed below and can be installed using `pip`:

```bash
pip install -r requirements.txt
```

**Requirements:**

| Package | Version |
| :--- | :--- |
| `Flask` | `3.0.0` |
| `google-generativeai` | `0.8.3` |
| `python-dotenv` | `1.0.1` |

### 4. Set Up Environment Variables

Create a `.env` file in your root directory and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

(You can refer to `.env.example` for guidance.)

### 5. Run the App

Start the application using the Python interpreter:

```bash
python app.py
```



## 💬 Example Queries

Try these sample queries in the chat bar:

*   “Top 5 best-selling products today”
*   “What was our total revenue yesterday?”
*   “Show me the sales trend for this week”
*   “Compare this week vs last week”
*   “Which products performed best in October?”

Each question triggers a contextual AI-driven response with relevant charts and metrics.

## 📊 Example Output

**User:** “Top 5 best-selling products today”

**Agent Response:**

*   Newport Box 100s — 1000 sold ($10,570.00)
*   McCormick 375ml — 1000 sold ($5,190.00)
*   Custom Item — 125 sold ($1,278.83)
*   Red Bull 8.4oz — 90 sold ($269.10)
*   The Perfect Gift — 80 sold ($1,600.00)

**💡 Insight:** “These five items contributed nearly 45% of today’s total sales.”

## 🧠 Design Decisions and Tech Stack

The following technologies and design choices were made to build the Sales Insight Agent:

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend** | Python Flask | Chosen for its simplicity and fast API integration. |
| **AI Model** | Google Gemini 2.5 Pro | Generates context-aware, human-like sales insights. |
| **Frontend** | HTML, CSS, JavaScript | Standard web technologies. |
| **Visualization** | Chart.js | Offers clean, dynamic data visualization. |
| **UI/Aesthetics** | Lottie, Responsive Gradient UI | Lottie animation enhances the UI aesthetics. |
| **Storage** | Browser localStorage | Used for persistent chips to keep recent user questions for a ChatGPT-style experience. |
| **Logic** | Intent detection | Ensures the app responds only with relevant sections (top items, trend, or summary). |

**Key Design Decisions:**

*   **Flask** was chosen for its simplicity and fast API integration.
*   **Gemini 2.5 Pro** generates context-aware, human-like sales insights.
*   **Intent detection** ensures the app responds only with relevant sections (top items, trend, or summary).
*   **Chart.js** offers clean, dynamic data visualization.
*   **Lottie animation** enhances the UI aesthetics.
*   **Persistent chips** keep recent user questions for good user  experience.
*   **Styling** uses a Responsive Gradient UI with animations.

## Reflection

### Most challenging aspect:
The hardest part was ensuring Gemini’s AI responses aligned perfectly with user intent. It required balancing natural language generation with accurate data parsing and aggregation from JSON-based sales data. Integrating contextual question understanding (like "compare this week vs last week") was also tricky.

### What would you improve:
If I had more time, I’d add authentication for multiple merchants, support live data streams (not static JSON), and include more visualizations like line charts and category-based breakdowns. A voice input feature would also make it more interactive.

### Interesting decisions:
A key decision was to make the UI and backend both intent-aware. Instead of dumping all data every time, the system intelligently decides whether to show totals, top products, or trends. Combining Gemini’s narrative output with factual metrics made the experience analytical yet conversational — just like interacting with a real business analyst.


## Bonus Features Implemented

This project includes all four optional enhancements mentioned in the technical requirements:

| Feature | Description | File(s) |
| :--- | :--- | :--- |
| 🧠 Multi-turn Conversations | The app remembers previous user queries and AI responses using Flask session-based memory. This allows natural, context-aware follow-up questions. | `app.py`, `llm_agent.py` |
| ⚡ Caching API Responses | Reduces API calls by caching recent results for 60 seconds to improve performance and reliability. | `sales_api.py` |
| 📅 Smart Date Parsing | Natural date terms like “today”, “yesterday”, “last week”, and “this month” are parsed automatically. | `utils.py` |
| 🧪 Automated Tests | Includes a minimal test suite to verify key routes and ensure the API and frontend logic respond correctly. | |
