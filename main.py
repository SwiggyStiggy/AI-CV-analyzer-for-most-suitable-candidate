import sys
import os
import dotenv
import openai
import fitz
import docx

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTextEdit, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Set your OpenAI API key here
dotenv.load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class AnalysisWorker(QThread):
    progress_update = pyqtSignal(int)
    result_ready = pyqtSignal(str)
    
    def __init__(self, folder_path, file_list, job_description):
        super().__init__()
        self.folder_path = folder_path
        self.file_list = file_list
        self.job_description = job_description
        
    def run(self):
        candidate_texts = {}
        total_files = len(self.file_list)
        for i, file_name in enumerate(self.file_list):
            file_path = os.path.join(self.folder_path, file_name)
            extracted_text = ""
            try:
                if file_name.lower().endswith(".pdf"):
                    doc = fitz.open(file_path)
                    for page in doc:
                        extracted_text += page.get_text()
                    doc.close()
                elif file_name.lower().endswith(".docx"):
                    doc = docx.Document(file_path)
                    extracted_text = "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                extracted_text = "Error extracting text: " + str(e)
            candidate_texts[file_name] = extracted_text
            progress_percent = int(((i + 1) / total_files) * 50)
            self.progress_update.emit(progress_percent)

    

        
        # Pre-structured and Pre-Built prompt
        prompt = (
            "You are a professional hiring assistant helping a company select the best candidate for a job role. "
            "Your goal is to analyze multiple candidate CVs and determine the **most suitable** person for the job. "
            "Use a structured and logical approach to ensure consistency.\n\n"
        )

        prompt += "📌 **Job Description:**\n" + self.job_description + "\n\n"

        prompt += "📂 **Candidate CVs:**\n"
        for file_name, text in candidate_texts.items():
            prompt += f"📄 **File:** {file_name}\n📝 **CV Content:** {text[:1000]}...\n\n"

        prompt += (
            "🛠 **Evaluation Criteria:**\n"
            "- Skills match with job description\n"
            "- Relevant work experience\n"
            "- Certifications or degrees\n"
            "- Achievements or special projects\n"
            "- Soft skills or leadership qualities\n\n"
        )

        prompt += (
            "🔍 **Your Task:**\n"
            "1️⃣ Carefully analyze each candidate based on the above criteria.\n"
            "2️⃣ Identify **one single best candidate** based on skills, experience, and qualifications.\n"
            "3️⃣ Provide a **detailed explanation** of why they are the best fit.\n"
            "4️⃣ Format the output in a structured way with bullet points.\n\n"
        )

        prompt += (
            "📢 **Final Answer Format:**\n"
            "**🏆 Best Candidate:** [Candidate Name]\n"
            "**🔹 Why They Are the Best:**\n"
            "- ✅ [Key strength 1]\n"
            "- ✅ [Key strength 2]\n"
            "- ✅ [Key strength 3]\n"
            "- ⚠️ [Potential Weakness (if applicable)]\n\n"
            "**📌 Runner-Ups:**\n"
            "- [Candidate 2] – [Brief reason]\n"
            "- [Candidate 3] – [Brief reason]\n"
        )

        # Midway progress update before API call
        self.progress_update.emit(55)

        
        # OpenAI API call
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", 
                     "content": "You are a professional career advisor specializing in matching candidates to job positions. "
                                "Your task is to carefully analyze CVs and job descriptions to select the most suitable candidate. "
                                "You evaluate candidates based on their skills, work experience, qualifications, achievements, and potential fit for the role."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
            )
            ai_result = response.choices[0].message['content']
        except Exception as e:
            ai_result = "Error during OpenAI API call: " + str(e)
        
        self.progress_update.emit(100)
        self.result_ready.emit(ai_result)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV Analyzer")
        self.setGeometry(100, 100, 1000, 600)
        
        # Main widget and overall layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        # Left column: Folder browsing and file list
        self.left_layout = QVBoxLayout()
        
        # 1st window: Folder display (small window)
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setFixedHeight(30)
        self.folder_label.setStyleSheet("border: 1px solid black;")
        self.left_layout.addWidget(self.folder_label)
        self.folder_label.setFixedSize(200, 50)
        
        # 2nd window: List of files (with extensions and numbering)
        self.contents_list = QListWidget()
        self.contents_list.setStyleSheet("border: 1px solid black;")
        self.left_layout.addWidget(self.contents_list)
        self.contents_list.setFixedSize(200, 500)
        
        # 1st button: Browse button
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        self.left_layout.addWidget(self.browse_button)
        self.browse_button.setFixedSize(80, 30)

        
        self.main_layout.addLayout(self.left_layout)
        
        # Right column: Job description and AI analysis output
        self.right_layout = QVBoxLayout()
        
        # 3rd window: Job description input (big window with placeholder)
        self.job_description_text = QTextEdit()
        self.job_description_text.setPlaceholderText("Please insert job description here...")
        self.right_layout.addWidget(self.job_description_text)
        
        # 4th window: AI analysis output (same size as job description window)
        self.analysis_output = QTextEdit()
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setPlaceholderText("AI analysis will be displayed here....")
        self.right_layout.addWidget(self.analysis_output)
        
        # 2nd button: Analyze button
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.start_analysis)
        self.right_layout.addWidget(self.analyze_button)
        self.analyze_button.setFixedSize(80, 30)
        
        self.main_layout.addLayout(self.right_layout)
        
        # Progress bar at the bottom (spanning across the window)
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setValue(0)
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addLayout(self.main_layout)
        self.vertical_layout.addWidget(self.progress_bar)
        self.main_widget.setLayout(self.vertical_layout)
        
        self.folder_path = ""
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(folder)
            self.populate_file_list()
    
    def populate_file_list(self):
        self.contents_list.clear()
        if self.folder_path:
            files = os.listdir(self.folder_path)
            # Filter for only .pdf and .docx files
            filtered_files = [f for f in files if f.lower().endswith((".pdf", ".docx"))]
            for idx, file in enumerate(filtered_files, 1):
                self.contents_list.addItem(f"{idx}. {file}")
            self.file_list = filtered_files  # Save the filtered list for analysis
    
    def start_analysis(self):
        if not self.folder_path:
            self.analysis_output.setPlainText("Please select a folder first.")
            return
        if not hasattr(self, 'file_list') or len(self.file_list) == 0:
            self.analysis_output.setPlainText("No valid CV files (.pdf or .docx) found in the selected folder.")
            return
        job_description = self.job_description_text.toPlainText().strip()
        if not job_description:
            self.analysis_output.setPlainText("Please enter a job description.")
            return
        
        self.analysis_output.clear()
        self.progress_bar.setValue(0)
        self.analyze_button.setEnabled(False)
        
        self.worker = AnalysisWorker(self.folder_path, self.file_list, job_description)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.result_ready.connect(self.display_result)
        self.worker.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def display_result(self, result):
        self.analysis_output.setPlainText(result)
        self.analyze_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
