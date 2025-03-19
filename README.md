AI-Powered CV Screening Tool

**General Overview**:
This project is an AI-powered CV screening tool built with PyQt6, OpenAI's GPT-3.5-Turbo, and document processing libraries.  
It scans .pdf and .docx CVs, matches them to a given job description, and selects the most suitable candidate with a detailed explanation.

**Features**:
Automatic CV Processing -  Extracts text from .pdf and .docx files
AI-integration - ses GPT-3.5-Turbo to analyze and candidates
Role-Based Evaluation - Provides structured, bullet-point justifications  

**Installation**:
1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Please do not forget to add your personal OpenAI API key in the .env file in order to run the ChatGPT part.
create a .env file in root directory and simply add: OPENAI_API_KEY=your_api_key_here

4.Run the application

**Guide**:
1. Select a folder containing CVs (.pdf or .docx)
2. Enter or paste a job description in the provided field

(There are 3 job description and 5 CV examples provided in the project, but you can use your own).

3. Click "Analyze" – The AI will evaluate and suggest the best candidate.
4. Review the results with structured bullet-point reasoning.

**Configuration Options**:
Temperature: Controls randomness (default: 0.3) (Used in this case)
Top-p: Limits word probability range (default: 0.7)(Not Used, but feel free to add it based on your preference)
Max Tokens: Sets response length (default: 1000)(Used and personally prefered this ammount)
**(Adjust these in config.py as needed)**

