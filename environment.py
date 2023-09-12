import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRETS = os.getenv('GITHUB_CLIENT_SECRETS')
REDIRECT_URL = os.getenv('REDIRECT_URL')
if OPENAI_API_KEY is None:
    raise Exception("API key not found in the .env file")

# to avoid the error message
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # or "true" depending on your needs
'''
This means the tokenizers library will attempt to use multiple threads to speed up tokenization processes.
However, if your environment involves forking processes, enabling parallelism can lead to potential issues like deadlocks (as described in the warning you provided).
'''

# Any remote API (OpenAI, Cohere etc.)
OPENAI_TIMEOUT = float(os.getenv("REMOTE_API_TIMEOUT_SEC", 30))
OPENAI_BACKOFF = float(os.getenv("REMOTE_API_BACKOFF_SEC", 10))
OPENAI_MAX_RETRIES = int(os.getenv("REMOTE_API_MAX_RETRIES", 5))
