import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

GROQ_BASE_URL = ""
groq_base_url =""
api_key = os.getenv(GROQ_API_KEY)
load_dotenv()
openai = OpenAI(base_url=groq_base_url, api_key=api_key)