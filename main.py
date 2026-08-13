import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import json
groq_base_url ="https://api.groq.com/openai/v1"
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
openai = OpenAI(base_url=groq_base_url, api_key=api_key)
model = "openai/gpt-oss-120b"

# def seek_assistant(message, history):
#     history = [{"role": h["role"], "content":h["content"]}, for h in history]
#     pass

# tiket_prices = {"london": "$100", "abuja": "$300", "lagos": "$50", "ibadan":"$50"}
# def get_ticket_price(destination):
#     price = tiket_prices.get (destination.lower(), "unknown price")
#     if price is not None:
#         ticket_details = f"the price for the ticket to {destination} is {price}"
#         return (ticket_details)
    
# print(get_ticket_price("warri"))

# def chat(message, history):
#     price_function ={}
#     system_message = "youre an helpful airline assistant"
#     tools = [{"type":"function", "function":price_function}]
#     history = [{"role": h["role"], "content": h["content"]} for h in history]
#     messages = [{"role":"system", "content": system_message} + history + {"role":"user", "content": message}]
#     response = openai.chat.completions.create(model = model, messages= messages, tools=tools)
    
#     if response.choices[0].finish_reason == "tool_call":
#         message= response.choices[0].message
#         result = tool_call(message)
#         messages.append(message)
#         message.append (result)
#         response = openai.chat.completions.create(model= model, messages= messages)
        
        
#     return response.choices[0].message.content





# this particular function is the manual way of gettiing a ticket price without having to involve an llm 

ticket_pice = {"lagos": "$500"}

def get_ticket_price(destination):
    price = ticket_pice.get(destination.lower(), "unknown price")
    return f"your ticket to {destination} is {price} "



system_message = """
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
"""

price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}
tools =[{"type":"function", "function": price_function}]

def handle_tool_calls(message):
    responses = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            price_details = get_ticket_price(city)
            responses.append({
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            })
    return responses


def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=model, messages=messages, tools=tools)

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        response = openai.chat.completions.create(model=model, messages=messages, tools=tools)
    
    return response.choices[0].message.content

gr.ChatInterface(fn = chat).launch(auth=("favour", "favour123"), inbrowser=True)