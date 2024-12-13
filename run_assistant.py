import hupper
import chatbot
from dotenv import load_dotenv, find_dotenv
import subprocess
import os

if __name__ == '__main__':
    load_dotenv(find_dotenv())

    venv_activate = os.path.join('.venv', 'Scripts', 'activate.bat')
    subprocess.Popen(f'call {venv_activate} && python mock_apis/mock_fitbit_api.py', shell=True)
    # Start the mock FitBit API server
    # subprocess.Popen(['python', 'mock_apis/mock_fitbit_api.py'])

    reloader = hupper.start_reloader('chatbot.main')  # Replace 'chatbot.main' with the function that launches your Fitness Agent Gradio app
    chatbot.main()
