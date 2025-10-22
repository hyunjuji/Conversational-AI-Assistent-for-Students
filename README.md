
# **AI Student Assistant**
### *Conversational AI Agent Support System for College Students*


## **Project Structure**

```bash
project/
├── app.py                  # Main application(Agent orchestration logic)
├── README.md
├── pyproject.toml / requirements.txt
├── data/                  # Local SQLite database files (excluded from Git)
├── credentials/           # Google API credentials and OAuth tokens (excluded from Git)
├── programs/              # Reference documents (excluded from Git)
├── src/
│   ├── gradio_app.py      # Gradio interface initialization
│   ├── gt_tools.py        # Tool registry and integration logic
│   ├── db_functions.py    # Database utility functions
│   ├── calendar_functions.py
│   ├── program_functions.py
│   └── ...
└── .env                   # Environment variables (excluded from Git)
```

---

## **Key Features**

| Feature                  | Description |
|-------------------------|-------------|
| AI Conversational Agent | Natural language interaction powered by Azure OpenAI |
| Academic Program Access | Provides degree requirements and program-specific details |
| Course Recommendation   | Suggests courses based on academic history and DB data |
| Calendar Automation     | Integrates with Google Calendar to create/delete events |
| Web Search Integration  | Uses DuckDuckGo as a fallback search tool |
| Local Database Support  | SQLite-based storage for academic information |

---

## **Installation**

### 1. Install Dependencies

Using uv:
```bash
uv sync
```

---

### 2. Environment Variables Setup

Create a `.env` file in the project root and include:

```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your_model_name
```

---

### 3. Google Calendar Setup (Optional)

Place your OAuth credential file at:
```
credentials/credentials.json
```
The first run will authenticate and generate a token file for the user automatically.

---

## **Running the Application**

```bash
uv run python app.py
```

The Gradio chat interface will open in your browser.

---

## **Security Notice**

The following files and directories are excluded from version control to protect sensitive information:

```
.env
credentials/
data/
programs/
*.json
*.db
```

Each user must configure these locally to run the application.

---

## **Database Usage Example**

```python
from src.db_functions import query_university_db

result = query_university_db("SELECT * FROM courses LIMIT 5;")
print(result)
```

---

## ## **License**

This project is intended for educational and research purposes. Sensitive data such as API keys and database files are not included in this repository.
