# Japanese Language Tech Stack & Dependencies

This document summarizes the key libraries and tools used in this project for Japanese language processing. Use this as a prompt or context when generating code or refining features (e.g., sentence generation).

## Backend (Python)

*   **`jamdict`**: A Python library for accessing the JMdict (vocabulary) and Kanjidic (kanji) databases. We use this for:
    *   Looking up word meanings and readings.
    *   identifying parts of speech.
    *   Searching for words by kana or kanji.
*   **`jamdict-data`**: The actual database file for `jamdict` containing the dictionaries.
*   **`mecab-python3`**: A Python wrapper for the MeCab morphological analyzer. We use this for:
    *   Tokenizing Japanese sentences (breaking them into words).
    *   Analyzing the structure of text for pitch accent generation.
*   **`unidic-lite`**: A lightweight dictionary for MeCab. It provides the statistical data needed for accurate tokenization.
*   **`fsrs`**: An implementation of the Free Spaced Repetition Scheduler. This algorithm powers our review system, calculating optimal intervals for flashcards.
*   **`rich`**: Used for pretty-printing debugging information and logs to the terminal.

## Frontend (React/Vite)

*   **`axios`**: Handles HTTP requests to our Python backend.
*   **`framer-motion`**: Used for smooth animations in the UI.
*   **`canvas-confetti`**: Generates confetti effects for rewards/celebrations.
*   **`lucide-react`**: Provides the icon set used throughout the application.

## Data & Architecture

*   **Genki I Vocabulary**: The database is seeded with vocabulary from the Genki I textbook.
*   **SQLite**: The application uses a local SQLite database (`data/vocab.db`) for storing user progress and dictionary data.
*   **FastAPI**: The backend framework that ties everything together.
