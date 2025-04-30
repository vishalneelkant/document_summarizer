Document Summarizer 

Prerequisites:
Python: Ensure Python 3.8 or higher is installed on your system. You can download it from python.org.
Virtual Environment: It is recommended to use a virtual environment to manage dependencies.
Streamlit: This project uses Streamlit for the frontend.
Install Required Libraries: The project depends on several Python libraries, including streamlit, langchain, and others.


Setup Instructions
1. Clone the Repository:
   git clone <repository-url>
   cd <repository-folder>
   
2. Create a Virtual Environment:
   python3 -m venv my_env
   source my_env/bin/activate  # On Mac/Linux
   # For Windows: my_env\Scripts\activate
   
3. Install Dependencies Install the required Python libraries using pip:
   pip install streamlit langchain faiss-cpu

Set Up the Project Structure Ensure the following directory structure exists:
project-root/
├── front-end/
│   ├── chat-ui-frontent-v2.py
├── back-end/
│   ├── backend.py
│   ├── attachments/
│       ├── offering.txt  # Add your default attachment file here
├── my_env/  # Virtual environment (ignored by .gitignore)
├── .gitignore


To run the project : 
  **streamlit run chat-ui-frontent-v2.py**
   
![image](https://github.com/user-attachments/assets/4057c5ee-1a2d-4f6c-9f8e-b13d44f9ae02)
