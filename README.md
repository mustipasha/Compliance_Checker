# Compliance Checker Tool

## Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key (set in `backend/.env`)

## Setup

1.  **Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    ```

## Running the Application

1.  **Start Backend**:
    ```bash
    cd backend
    python main.py
    ```
    The API will be available at `http://localhost:8000`.

2.  **Start Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```
    The UI will be available at `http://localhost:5173`.

## Usage
1.  Open the Frontend URL.
2.  Upload your System Documentation (PDF).
3.  Wait for the assessment to complete.
4.  View the compliance report.
