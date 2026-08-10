import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

import gradio as gr

api_key = os.getenv("GROQ_API_KEY")
groq_base_url = "https://api.groq.com/openai/v1"
model = "openai/gpt-oss-120b"

openai = OpenAI(base_url= groq_base_url, api_key=api_key)

system_message = """
You are a helpful assistant in a clothes store. You should try to gently encourage \
the customer to try items that are on sale. Hats are 60% off, and most other items are 50% off. \
For example, if the customer says 'I'm looking to buy a hat', \
you could reply something like, 'Wonderful - we have lots of hats - including several that are part of our sales event.'\
Encourage the customer to buy hats if they are unsure what to get. If the customer asks for shoes, you should respond that shoes are not on sale today, \
but remind the customer to look at hats!"
"""

def chat(message, history):
    history = [{"role":item["role"], "content":item["content"]} for item in history]
    message = [{"role":"system", "content":system_message}] + history + [{"role":"user", "content": message}]
    response = openai.chat.completions.create(model = model, messages=message, stream=True)
    results = ""
    for chunks in response:
        results += chunks.choices[0].delta.content or ""
        yield results
        
        
    
    
input = gr.Textbox(label= "we've got you, what do you nee dhelp with?", lines=2)
output = gr.Markdown()

# view = gr.ChatInterface(
#     fn= chat,
#     title= 'welcome back',
#     inputs= [input],
#     outputs= [output],
#     flagging_mode="never",
# )

view = gr.ChatInterface(fn = chat).launch(inbrowser=True, auth=True)