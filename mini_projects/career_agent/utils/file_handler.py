import os
from datetime import datetime

def save_file(data, filename):
    """saves data to a markdown file"""
    folder_name = "Agent_output"
    os.makedirs(folder_name, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{filename}_{timestamp}.md"
    file_path = os.path.join(folder_name, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)
    return file_path 