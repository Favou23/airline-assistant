import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

GROQ_BASE_URL = ""
groq_base_url =""
api_key = os.getenv(GROQ_API_KEY)
load_dotenv()
openai = OpenAI(base_url=groq_base_url, api_key=api_key)
model = "openai/gpt-oss-120b"

def seek_assistant(message, history):
    history = [{"role": h["role"], "content":h["content"]}, for h in history]
    pass

tiket_prices = {"london": "$100", "abuja": "$300", "lagos": "$50", "ibadan":"$50"}
def get_ticket_price(destination):
    price = tiket_prices.get (destination.lower(), "unknown price")
    if price is not None:
        ticket_details = f"the price for the ticket to {destination} is {price}"
        return (ticket_details)
    
print(get_ticket_price("warri"))

def chat(message, history):
    price_function ={}
    system_message = "youre an helpful airline assistant"
    tools = [{"type":"function", "function":price_function}]
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [{"role":"system", "content": system_message} + history + {"role":"user", "content": message}]
    response = openai.chat.completions.create(model = model, messages= messages, tools=tools)
    
    if response.choices[0].finish_reason == "tool_call":
        message= response.choices[0].message
        result = tool_call(message)
        messages.append(message)
        message.append (result)
        response = openai.chat.completions.create(model= model, messages= messages)
        
        
    return response.choices[0].message.content

def tool_call():
    pass
        
        
        
        