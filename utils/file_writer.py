import os

class FileWriter:
    @staticmethod
    def write(filepath: str, content: str)-> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)