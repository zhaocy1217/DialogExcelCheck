class ReturnCode:
    success = True
    error_content = ""
    def __init__(self, success: bool, error_content: str):
        self.success = success
        self.error_content = error_content
    def __str__(self):
        return f"success: {self.success}, error_content: {self.error_content}"
