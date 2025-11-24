# Role: Senior Python AI Engineer

**Objective:** Build a "PDF Study Companion" (Summarizer & Quizzer) using Chainlit, PyPDF, and Google Gemini.

## 1\. Project Overview

The goal is to develop an educational tool that processes PDF uploads to provide summaries and generate quizzes based on the document content.

  * **UI:** Chainlit (Modern, responsive web interface).
  * **Model:** Google Gemini model named `gemini-2.5-flash` (via Google Generative AI SDK).
  * **Extraction:** `pypdf` library for text extraction.
  * **State Management:** Chainlit User Session (to store text for the quiz step).

## 2\. Critical Technical Constraints

**You must adhere to the following strict configuration rules:**

1.  **Zero-Bloat Protocol (CRITICAL):**
      * **Do NOT write extra code.** No complex vector databases (RAG) or LangChain frameworks unless necessary. Use direct text context.
      * **Focus strictly on the flow:** Upload -\> Extract -\> Summarize -\> Quiz.
      * **No "Hallucinated" Features:** If it is not in the `chainlit` or `google-generativeai` docs, do not invent it.
2.  **API Configuration:**
      * Use the official `google-generativeai` Python Library.
      * **API Key:** Load `GEMINI_API_KEY` from environment variables.
      * **Model:** Use `gemini-2.5-flash`.
3.  **Text Extraction:**
      * You **MUST** use `pypdf` to extract text from the uploaded file bytes.
      * Handle the text as a standard string.
4.  **Error Recovery Protocol:**
      * If you encounter a `TypeError` or file reading error, **STOP**.
      * Verify how Chainlit passes file objects (bytes vs path) before rewriting.
5.  **Dependency Management:** Use `uv` for package management.

## 3\. Architecture & File Structure

*Note: The current directory is the root. Do not create a subfolder.*

```text
.
├── .env                  # Environment variables (API Key)
├── pdf_ops.py            # PyPDF extraction logic
├── app.py                # Chainlit UI & Event Handlers
└── pyproject.toml        # UV Config
```

## 4\. Implementation Steps

**Follow this exact logical flow. Do not skip steps.**

### Step 1: Documentation & Pattern Analysis

**Before writing code, verify the libraries.**

1.  **Action:** Use the MCP tool `get-library-docs` for **`chainlit`** (specifically file upload handling) and **`pypdf`**.
2.  **Analysis:**
      * How does `cl.AskFileMessage` return the file object?
      * How does `pypdf.PdfReader` handle BytesIO streams?
      * **Check:** Ensure you understand how to store the extracted text in `cl.user_session` so it can be reused for the quiz later.

### Step 2: PDF Processing (`pdf_ops.py`)

Create the extraction logic.

  * **Function:** `extract_text_from_pdf(file_bytes) -> str`
  * **Logic:**
      * Initialize `PdfReader` with the file stream.
      * Iterate through pages and append text to a string.
      * Clean the text (remove excessive whitespace).
      * Return the full text.

### Step 3: UI & Application Logic (`app.py`)

Integrate Chainlit with the specific A/B flow.

  * **`@cl.on_chat_start`**:

      * Send a `cl.AskFileMessage` requesting a PDF.
      * Wait for the file. Once uploaded, call `extract_text_from_pdf`.
      * **State Storage:** Save the full extracted text to `cl.user_session.set("pdf_text", text)`.
      * **Trigger Summary:** Immediately send the text to Gemini with a system prompt to "Summarize this document structured for students."
      * **Display Options:** Send a `cl.Message` containing the summary.
      * **Next Action:** Send a `cl.Action` button labeled "Create Quiz".

  * **`@cl.action_callback("create_quiz")`**:

      * Retrieve the original text from `cl.user_session.get("pdf_text")`.
      * **Prompt:** Send a request to Gemini: "Generate a mixed-style quiz (MCQ and Open Ended) based on this text."
      * Display the result in the chat.

### Step 4: Environment & Dependencies

  * Create a `.env` template.
  * List necessary packages in `pyproject.toml` (`chainlit`, `google-generativeai`, `pypdf`).
  * **Smart Install:** Check if dependencies exist before running install commands.

## 5\. Testing Scenarios

1.  **Upload Flow:** User uploads `lecture.pdf` -\> App displays "Processing..." -\> App returns a formatted Summary.
2.  **State Persistence:** User reads summary -\> Clicks "Create Quiz" button -\> App accesses the *original* text (without re-uploading) and generates questions.
3.  **Context Limits:** If text is too long, ensure the prompt includes an instruction to "Summarize the first 10,000 characters" (basic truncation for safety, if needed).