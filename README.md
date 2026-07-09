#  Autonomous Insurance Claims Processing Agent

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)

An AI-powered insurance claims processing system designed to automate the **First Notice of Loss (FNOL)** workflow. The application intelligently extracts key claim information from TXT and PDF documents, validates mandatory fields, detects incomplete or inconsistent data, and recommends the most appropriate claims processing route using deterministic business rules.

The system combines the flexibility of Large Language Models (LLMs) for document understanding with a reliable rule-based decision engine, ensuring accurate, transparent, and consistent claim routing for every submission.

---

# 🤖 Why This Is an AI Agent

Unlike traditional parsers that rely on fixed templates or hardcoded formats, this application uses an **Ollama Cloud Large Language Model (LLM)** to understand FNOL documents written in different layouts, formats, and natural language styles.

The AI agent is responsible for:

- Extracting structured information from unstructured insurance documents.
- Understanding varying document layouts and wording.
- Returning standardized claim information in a consistent JSON format.

If the AI model is unavailable or returns invalid output, the application automatically switches to a **regex-based extraction engine**, ensuring uninterrupted processing without affecting the user experience.

---

# ⚖️ Reliable Rule-Based Claim Routing

While AI is used for information extraction, **claim routing is intentionally performed using deterministic business rules rather than the LLM**.

This design provides several important advantages:

- ✅ Consistent and repeatable routing decisions.
- ✅ No hallucinations or unpredictable AI behaviour during business-critical decisions.
- ✅ Fully transparent and explainable routing logic.
- ✅ Easy auditing and compliance with insurance business processes.
- ✅ Reliable performance even when the LLM service is unavailable.

Each routing recommendation includes a clear explanation describing **exactly which rule triggered the decision**, making every result easy to understand and verify.

---

# 📊 Excel Audit Logging

Every processed claim is automatically recorded in **`claims_log.xlsx`**, providing a complete audit trail of all processed insurance claims.

The Excel logger automatically:

- Creates the workbook if it does not already exist.
- Records every extracted claim field.
- Stores missing mandatory fields.
- Saves the recommended routing decision.
- Logs the reasoning behind every decision.
- Records the extraction method (LLM or Regex Fallback).
- Stores confidence information and processing timestamps.
- Maintains a permanent audit history for future review.

Depending on your logging configuration, claims can either:

- Append new claims as separate records, or
- Update existing claims using the Policy Number as the unique identifier.

The logging module is completely isolated from the main processing pipeline. If Excel is unavailable (for example, if the workbook is currently open or locked), the application continues processing claims normally and still returns the final routing decision without interruption.

This architecture ensures that reporting failures never impact the core claims processing workflow.

## ✨ Features

- AI-assisted extraction using Ollama Cloud
- Automatic regex fallback
- TXT & PDF support
- Streamlit dashboard
- Rule-based routing engine
- Excel audit log
- JSON output
- PDF report generation
- Missing field detection
- Deterministic routing

---

## 🏗 Architecture

```text
FNOL Document
      │
      ▼
 Streamlit UI
      │
      ▼
LLM Extraction
      │
      ├── Success
      └── Regex Fallback
             │
             ▼
 Field Validation
             ▼
 Routing Engine
             ▼
 Excel Log + JSON + PDF
```

## 📁 Project Structure

```text
Insurance_Agent/
├── app.py
├── pipeline.py
├── extractor.py
├── llm_client.py
├── router.py
├── schema.py
├── excel_logger.py
├── requirements.txt
├── GUIDE.md
├── README.md
├── .env.example
├── sample_fnols/
└── claims_log.xlsx
```

## 🚀 Installation

```bash
git clone https://github.com/chandan-me/Autonomous-Insurance-Claims-Processing-Agent.git
cd Autonomous-Insurance-Claims-Processing-Agent

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file:

```env
OLLAMA_API_KEY=YOUR_API_KEY
```

If no API key is available, the application automatically switches to regex extraction.

## ▶️ Run

```bash
streamlit run app.py
```
## Complete Flow
```
      User Opens App
            │
            ▼
      Upload TXT / PDF
            │
            ▼
      Read File
            │
            ▼
      Process Claim
            │
            ▼
      run_fnol_agent()
            │
            ▼
      Pipeline
            │
            ▼
      Extraction
            │
            ▼
      Validation
            │
            ▼
      Routing
            │
            ▼
      Excel Logger
            │
            ▼
      Return JSON
            │
            ▼
      Display Dashboard
            │
            ▼
      Download PDF || Download JSON
```

## 📋 Routing Rules

| Condition | Route |
|-----------|-------|
| Missing mandatory fields | Manual Review |
| fraud / staged / inconsistent | Investigation Flag |
| Claim Type = Injury | Specialist Queue |
| Damage < ₹25,000 | Fast-track |
| Otherwise | Standard Review |

## 📊 Dashboard

Displays:

- Claim Status
- Confidence
- Risk Level
- Recommended Route
- Missing Fields
- Extracted Fields
- Decision Reasoning
- Download JSON
- Download PDF

## 📈 Excel Logging

Each processed claim stores:

- Claim ID
- Policy Number
- Claim Status
- Recommended Route
- Confidence
- Risk Level
- Missing Fields
- Reasoning
- Timestamp

## 🛠 Technologies

- Python
- Streamlit
- Ollama Cloud API
- Pydantic
- Requests
- PDFPlumber
- OpenPyXL
- Pandas
- Plotly
- ReportLab

## 🧪 Test

```bash
python pipeline.py sample_fnols/claim1_fasttrack.txt
```

## 🔒 Reliability

- Regex fallback
- Deterministic routing
- Graceful error handling
- Isolated Excel logging

## 🌟 Future Work

- OCR
- Image upload
- Fraud scoring
- REST API
- Docker
- Authentication
- Analytics Dashboard

## 👨‍💻 Author

**Chandan N**

GitHub: https://github.com/chandan-me

Email: chandan2004.n@gmail.com

Portfolio: https://www.chandan-n.me/
