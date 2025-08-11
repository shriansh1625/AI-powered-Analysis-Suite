Contextualizer Pro: AI-Powered Content Analysis Suite -
Contextualizer Pro is a sophisticated, full-stack web application designed to provide deep, multi-faceted analysis of web content. Built with a professional, scalable architecture, this tool serves as an intelligent lens for the modern web, empowering users to understand the context, sentiment, and authenticity of any article, image, or claim.

This project was developed by Shriansh Vikram Singh as a comprehensive demonstration of modern web development, AI integration, and professional software architecture patterns.

✨ Key Features
Contextualizer Pro is a multi-tool suite that offers three distinct analysis functions in a sleek, tabbed interface:

1. URL Analyzer
The core feature for deep-diving into news articles, blog posts, or any web page.

Multi-Language Support: Automatically detects the article's language (langdetect) and adapts its analysis.

Sentiment Analysis: For English articles, it generates a dynamic Radar Chart (Chart.js) visualizing the text's Polarity, Subjectivity, and Neutrality.

Named Entity Recognition (NER): Uses spaCy to identify and categorize key entities like People, Organizations, and Places mentioned in the text.

AI Deep Dive: Leverages the Google Gemini API to provide a sophisticated, narrative analysis of the article's tone, potential bias, and writing style.

One-Click Summarization: An on-demand button that uses the Gemini API to generate a concise, one-paragraph summary of the article.

Global Cross-Reference: Uses the SerpApi to search for the article's title across the web, showing what other sources are saying about the same topic.

Core Metrics: Calculates estimated reading time.

2. Image Analyzer
A powerful tool for combating visual misinformation.

AI Image Description: Uses the Gemini Vision model to provide a detailed, human-like description of the uploaded image.

Optical Character Recognition (OCR): Reads and extracts any text found within the image.

Reverse Image Search: Uses SerpApi's Google Lens engine to find where else the image has appeared online, helping to spot if it's being used out of context.

3. Fact-Check Tool
A targeted utility for verifying specific claims.

Claim Verification: Allows users to input a specific claim (e.g., "The moon is made of cheese.").

Targeted Search: Uses SerpApi to perform a targeted search for that exact claim across a pre-defined list of reputable fact-checking websites like Reuters, AP News, and Snopes.

User & UI Features
Secure User Authentication: Full login, signup, and logout functionality using Flask-Login with hashed passwords.

Stunning UI: A modern, animated frontend with a dynamic, interactive background powered by Vanta.js.

Light/Dark Theme: A seamless theme switcher that saves the user's preference.

Personalized "About Me" Modal: A professional pop-up showcasing the creator's profile and links.

🛠️ Tech Stack & Architecture
This application is built with an industry-standard, scalable architecture designed for performance and reliability.

Languages & Frameworks
Python: The core backend language.

Flask: A powerful micro-framework for the web server, using the Application Factory pattern for scalability.

JavaScript (ES6+): For all dynamic frontend logic, including API calls and DOM manipulation.

HTML5 & CSS3: For structuring and styling the application.

Backend Technologies
Celery: An asynchronous task queue used to run all heavy analysis (API calls, text processing) in the background, ensuring the UI remains fast and responsive.

Redis: A high-performance, in-memory key-value store used as the message broker for Celery.

Flask-SQLAlchemy: An ORM for elegant and secure database interactions.

Flask-Login & Werkzeug: For secure user session management and password hashing.

Gunicorn (for deployment): A production-ready WSGI server.

Frontend Technologies & Libraries
Bootstrap 5: For a modern, responsive, and mobile-first layout.

Chart.js: For creating beautiful and informative data visualizations (Sentiment Radar Chart).

Vanta.js & three.js: For the stunning, interactive animated background.

Animate.css: For smooth and engaging CSS animations.

APIs & AI Services
Google Gemini API: The core AI engine for the "Deep Dive," summarization, image description, and OCR.

SerpApi: Powers the Global Cross-Reference and Fact-Checking tools by providing real-time Google Search results.

spaCy & TextBlob: For Natural Language Processing (NLP) tasks like Named Entity Recognition and Sentiment Analysis.

Newspaper3k & langdetect: For article scraping and language detection.

Infrastructure & Testing
Docker: Used to containerize and manage the Redis server for consistency across environments.

Pytest: For writing and running automated unit tests to ensure code quality and reliability.

🚀 Setup and Installation
To run this project locally, follow these steps:

Clone the repository:
git clone https://github.com/shriansh1625/Contextualizer-Pro.git
cd Contextualizer-Pro

Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install all required libraries:

pip install -r requirements.txt
python -m spacy download en_core_web_sm

Set up your Environment Variables:

Create a file named .env in the root of the project.

Add your secret keys to this file. Use absolute paths with forward slashes for the database.

DATABASE_URL="sqlite:///C:/path/to/your/project/contextualizer.db"
SERPAPI_KEY="your_serpapi_key"
GEMINI_API_KEY="your_gemini_api_key"
SECRET_KEY="generate_a_strong_random_string_here"

Start Docker: Make sure you have Docker Desktop installed and presently running

Run the Services (in 3 separate terminals):

Terminal 1: Start Redis

docker run -d -p 6379:6379 redis

Terminal 2: Start the Celery Worker (Use -P eventlet for Windows)

python -m celery -A celery_worker.celery_app worker -l info -P eventlet

Terminal 3: Initialize the Database & Run the App

# Run this only once to create the database
flask init-db

# Start the web server
python app.py

