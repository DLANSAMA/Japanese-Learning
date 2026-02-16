# Japanese Learning App

A full-stack application for learning Japanese, featuring a spaced repetition system (SRS), vocabulary quizzes, and gamification elements.

## Prerequisites

Before you begin, ensure you have the following installed on your computer:

*   **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
*   **Node.js 18+**: [Download Node.js](https://nodejs.org/)

## Quick Start Walkthrough

Follow these steps to get the application running fully on your local machine.

### 1. Backend Setup

First, set up the Python backend and database.

1.  **Open a terminal** in the root directory of this project.

2.  (Optional but recommended) **Create a virtual environment**:
    ```bash
    python -m venv venv

    # Windows
    venv\Scripts\activate

    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Seed the Database**:
    This will populate the database with vocabulary from Genki I.
    ```bash
    python -m src.seed_genki
    ```
    *You should see a message confirming the database was updated.*

### 2. Frontend Setup

Next, set up the React frontend.

1.  **Open a new terminal window** (keep the first one open).

2.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

3.  **Install Node dependencies**:
    ```bash
    npm install
    ```

### 3. Running the Application

Now, you will run both the backend server and the frontend development server.

1.  **Start the Backend Server** (in your first terminal):
    ```bash
    python learn.py serve
    ```
    *Look for the output:* `API Key: <YOUR_KEY_HERE>`. **Copy this key**, you will need it!

2.  **Start the Frontend Server** (in your second terminal, inside `frontend/` folder):
    ```bash
    npm run dev
    ```

3.  **Access the App**:
    *   Open your browser and go to the URL shown in the frontend terminal (usually `http://localhost:5173`).
    *   The app might ask for authentication.
    *   **Paste the API Key** you copied from the backend terminal.

## Troubleshooting

*   **"Authentication Required"**: If the app asks for an API Key and you missed it, check the terminal running `python learn.py serve`. The key is printed inside a box of `=` signs at startup. You can also find it in `data/secrets.json`.
*   **Database Errors**: If you see errors about missing data, ensure you ran the seeding command: `python -m src.seed_genki`.
*   **Module Not Found**: Ensure you are running python commands from the **root** directory of the project, not inside `src/`.

## Key Features

*   **Dashboard**: Overview of your progress.
*   **Learn**: Study new vocabulary with pitch accent info.
*   **Quiz**: Test your knowledge with SRS-based quizzes.
*   **Dictionary**: Search for words and add them to your learning list.
*   **Settings**: Customize your experience.
