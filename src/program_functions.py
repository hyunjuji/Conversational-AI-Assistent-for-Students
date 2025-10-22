from PyPDF2 import PdfReader
import os


class gtProgramManager:
    def __init__(self):
        pass

    def get_program_details(self, program_name):
        base_dir = os.path.dirname(__file__)
        program_folder_path = os.path.join(base_dir,"programs",program_name)
        
        if not os.path.exists(program_folder_path):
            print("program folder does not exist")
            return f"Program {program_name} does not exist."
        
        file_contents = []

        for file in os.listdir(program_folder_path):
            if file.endswith(".pdf"):
                file_path = os.path.join(program_folder_path, file)
                try: 
                    reader = PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    text = text.replace('\n', ' ').replace('\r', '')
                    file_contents.append(text)
                except Exception as e:
                    print(f"[error occurred] {file}: {e}")
        if not file_contents:
            return f"No Program details found in the program folder: {program_name}"
        
        return file_contents
