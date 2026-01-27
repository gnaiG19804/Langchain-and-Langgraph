import configparser
import os

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        

        config_path = os.path.join(current_dir, 'uiconfigefile.ini')
        
        read_files = self.config.read(config_path)
        
        if not read_files:
            raise FileNotFoundError(f"❌ Không tìm thấy file config tại: {config_path}. Hãy kiểm tra lại xem bạn đã tạo file config.ini ở đúng chỗ chưa!")

    def get_page_title(self):
        return self.config['DEFAULT']['PAGE_TITLE']

    def get_llm_options(self):
        return self.config['DEFAULT']['LLM_OPTIONS'].split(',')

    def get_usecase_options(self):
        return self.config['DEFAULT']['USECASE_OPTIONS'].split(',')

    def get_groq_model_options(self):
        return self.config['DEFAULT']['GROQ_MODEL_OPTIONS'].split(',')