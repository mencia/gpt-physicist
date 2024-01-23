"""The purpose of this script is to have gpt-4 analyse pdfs. I need it to parse equations and analyse them."""
import openai
import requests
from dotenv import load_dotenv, find_dotenv
import os

# Access the API key
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv(find_dotenv())

def upload_file(file_path):
    """Function to upload a file"""
    headers = {
        'Authorization': f'Bearer {openai.api_key}'
    }

    response = requests.post(
        'https://api.openai.com/v1/files',
        headers=headers,
        files={
            'file': open(file_path, 'rb'),
            'purpose': 'answers'
        }
    )

    return response.json()

if __name__ == "__main__":

    load_environment()

    file_path = './papers/menciauranga2018.pdf'

    # Replace 'your-file-path.pdf' with the path to your PDF
    file_response = upload_file(file_path)

    print(file_response)
    import sys; sys.exit(0)

    # Check if the file was uploaded successfully
    if file_response.get('id'):
        file_id = file_response['id']
        print(f"File uploaded successfully. File ID: {file_id}")

        # Now you can use this file_id with OpenAI's language model
        # to analyze the content, ask questions, etc.

        # Example: Using the file for a question-answering task
        answer = openai.Answer.create(
            model="text-davinci-002",
            file=file_id,
            question="What is the main topic of the document?",
            search_model="text-davinci-002",
            max_rerank=10,
            max_tokens=50,
            stop=["\n", "<|endoftext|>"],
            temperature=0
        )

        print(answer['answers'][0])
    else:
        print("File upload failed.")
