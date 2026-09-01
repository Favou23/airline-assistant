# import os
# from dotenv import load_dotenv
# from openai import OpenAI
# import gradio as gr
# import json
# groq_base_url ="https://api.groq.com/openai/v1"
# load_dotenv()
# api_key = os.getenv("GROQ_API_KEY")
# openai = OpenAI(base_url=groq_base_url, api_key=api_key)
# model = "openai/gpt-oss-120b"


# ticket_pice = {"lagos": "$500"}

# def get_ticket_price(destination):
#     price = ticket_pice.get(destination.lower(), "unknown price")
#     return f"your ticket to {destination} is {price} "



# system_message = """
# You are a helpful assistant for an Airline called FlightAI.
# Give short, courteous answers, no more than 1 sentence.
# Always be accurate. If you don't know the answer, say so.
# """

# price_function = {
#     "name": "get_ticket_price",
#     "description": "Get the price of a return ticket to the destination city.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "destination_city": {
#                 "type": "string",
#                 "description": "The city that the customer wants to travel to",
#             },
#         },
#         "required": ["destination_city"],
#         "additionalProperties": False
#     }
# }
# tools =[{"type":"function", "function": price_function}]

# def handle_tool_calls(message):
#     responses = []
#     for tool_call in message.tool_calls:
#         if tool_call.function.name == "get_ticket_price":
#             arguments = json.loads(tool_call.function.arguments)
#             city = arguments.get('destination_city')
#             price_details = get_ticket_price(city)
#             responses.append({
#                 "role": "tool",
#                 "content": price_details,
#                 "tool_call_id": tool_call.id
#             })
#     return responses


# def chat(message, history):
#     history = [{"role":h["role"], "content":h["content"]} for h in history]
#     messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
#     response = openai.chat.completions.create(model=model, messages=messages, tools=tools)

#     while response.choices[0].finish_reason=="tool_calls":
#         message = response.choices[0].message
#         responses = handle_tool_calls(message)
#         messages.append(message)
#         messages.extend(responses)
#         response = openai.chat.completions.create(model=model, messages=messages, tools=tools)
    
#     return response.choices[0].message.content

# gr.ChatInterface(fn = chat).launch(auth=("favour", "favour123"), inbrowser=True)




import os
import json
import sqlite3
import base64

from io import BytesIO

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import gradio as gr


# ============================================================
# 1. ENVIRONMENT + CLIENTS
# ============================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")



# Groq client
groq_base_url = "https://api.groq.com/openai/v1"

groq = OpenAI(
    base_url=groq_base_url,
    api_key=groq_api_key
)



# ============================================================
# 2. MODEL CONFIGURATION
# ============================================================

CHAT_MODEL = "openai/gpt-oss-120b"

IMAGE_MODEL ="openai/gpt-oss-120b"

AUDIO_MODEL = "openai/gpt-oss-120b"


# ============================================================
# 3. DATABASE
# ============================================================

DB = "prices.db"


# ------------------------------------------------------------
# Create a small database for learning purposes
# ------------------------------------------------------------

def create_database():

    with sqlite3.connect(DB) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                city TEXT PRIMARY KEY,
                price INTEGER
            )
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO prices (city, price)
            VALUES (?, ?)
        """, ("lagos", 500))

        cursor.execute("""
            INSERT OR REPLACE INTO prices (city, price)
            VALUES (?, ?)
        """, ("london", 799))

        cursor.execute("""
            INSERT OR REPLACE INTO prices (city, price)
            VALUES (?, ?)
        """, ("paris", 899))

        cursor.execute("""
            INSERT OR REPLACE INTO prices (city, price)
            VALUES (?, ?)
        """, ("tokyo", 1400))

        cursor.execute("""
            INSERT OR REPLACE INTO prices (city, price)
            VALUES (?, ?)
        """, ("berlin", 499))

        conn.commit()


create_database()


# ============================================================
# 4. SYSTEM MESSAGE
# ============================================================

system_message = """
You are a helpful assistant for an Airline called FlightAI.

Give short, courteous answers, no more than 1 sentence.

Always be accurate.

If you don't know the answer, say so.

You have access to tools that can help you retrieve information.
Use the appropriate tool when necessary.
"""


# ============================================================
# 5. TOOL FUNCTION
# ============================================================

def get_ticket_price(destination_city):

    print(
        f"DATABASE TOOL CALLED: Getting price for {destination_city}",
        flush=True
    )

    with sqlite3.connect(DB) as conn:

        cursor = conn.cursor()

        cursor.execute(
            "SELECT price FROM prices WHERE city = ?",
            (destination_city.lower(),)
        )

        result = cursor.fetchone()

    if result:
        return f"Ticket price to {destination_city} is ${result[0]}"

    return "No price data available for this city"


# ============================================================
# 6. TOOL SCHEMA
# ============================================================

price_function = {

    "name": "get_ticket_price",

    "description": (
        "Get the price of a return ticket to the destination city."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "destination_city": {

                "type": "string",

                "description": (
                    "The city that the customer wants to travel to"
                )
            }
        },

        "required": [
            "destination_city"
        ],

        "additionalProperties": False
    }
}


# ============================================================
# 7. AVAILABLE TOOLS
# ============================================================

tools = [
    {
        "type": "function",
        "function": price_function
    }
]


# ============================================================
# 8. TOOL CALL HANDLER
# ============================================================

def handle_tool_calls(message):

    responses = []

    for tool_call in message.tool_calls:

        if tool_call.function.name == "get_ticket_price":

            # The model sends arguments as a JSON string.
            # Convert that JSON string into a Python dictionary.
            arguments = json.loads(
                tool_call.function.arguments
            )

            # Extract the destination city.
            city = arguments.get("destination_city")

            # Execute our actual Python tool.
            price_details = get_ticket_price(city)

            # Package the tool result in the format
            # expected by the LLM.
            responses.append({

                "role": "tool",

                "content": price_details,

                "tool_call_id": tool_call.id
            })

    return responses


# ============================================================
# 9. IMAGE GENERATION TOOL
# ============================================================

def artist(city):

    print(
        f"IMAGE TOOL CALLED: Generating image for {city}",
        flush=True
    )

    image_response = groq.images.generate(

        model=IMAGE_MODEL,

        prompt=(
            f"An image representing a vacation in {city}, "
            f"showing tourist spots and everything unique about {city}, "
            "in a vibrant pop-art style"
        ),

        size="1024x1024",

        n=1
    )

    # Extract the base64 image returned by OpenAI.
    image_base64 = image_response.data[0].b64_json

    # Convert base64 → bytes.
    image_data = base64.b64decode(image_base64)

    # Convert bytes → PIL Image.
    image = Image.open(
        BytesIO(image_data)
    )

    return image


# ============================================================
# 10. TEXT-TO-SPEECH
# ============================================================

# def talker(message):

#     print(
#         "AUDIO TOOL CALLED: Generating speech",
#         flush=True
#     )

#     response = groq.audio.speech.create(

#         model=AUDIO_MODEL,

#         voice="onyx",

#         input=message
#     )

#     return response.content


# ============================================================
# 11. TOOL HANDLER FOR MULTIMODAL VERSION
# ============================================================

def handle_tool_calls_and_return_cities(message):

    responses = []

    cities = []

    for tool_call in message.tool_calls:

        if tool_call.function.name == "get_ticket_price":

            # Convert JSON arguments → Python dictionary
            arguments = json.loads(
                tool_call.function.arguments
            )

            # Extract city
            city = arguments.get("destination_city")

            # Keep track of the city.
            # We will use this later to generate the image.
            cities.append(city)

            # Actually execute the database tool.
            price_details = get_ticket_price(city)

            # Package the result for the LLM.
            responses.append({

                "role": "tool",

                "content": price_details,

                "tool_call_id": tool_call.id
            })

    return responses, cities


# ============================================================
# 12. MAIN AI CHAT FUNCTION
# ============================================================

def chat(history):

    # --------------------------------------------------------
    # Convert Gradio history into OpenAI-style messages
    # --------------------------------------------------------

    history = [
        {
            "role": h["role"],
            "content": h["content"]
        }
        for h in history
    ]


    # --------------------------------------------------------
    # Build the initial conversation
    # --------------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ] + history


    # --------------------------------------------------------
    # First LLM call
    # --------------------------------------------------------

    response = groq.chat.completions.create(

        model=CHAT_MODEL,

        messages=messages,

        tools=tools
    )


    # --------------------------------------------------------
    # Keep handling tools until the LLM no longer asks
    # for one.
    # --------------------------------------------------------

    cities = []

    while response.choices[0].finish_reason == "tool_calls":

        # ----------------------------------------------------
        # Get the assistant message containing the tool call
        # ----------------------------------------------------

        message = response.choices[0].message


        # ----------------------------------------------------
        # Execute the requested Python tools
        # ----------------------------------------------------

        responses, tool_cities = (
            handle_tool_calls_and_return_cities(message)
        )


        # Keep track of cities returned by tools.
        cities.extend(tool_cities)


        # ----------------------------------------------------
        # Add the assistant's tool-call message
        # to the conversation
        # ----------------------------------------------------

        messages.append(message)


        # ----------------------------------------------------
        # Add the tool results
        # ----------------------------------------------------

        messages.extend(responses)


        # ----------------------------------------------------
        # Ask the LLM to continue now that it has
        # the tool result.
        # ----------------------------------------------------

        response = groq.chat.completions.create(

            model=CHAT_MODEL,

            messages=messages,

            tools=tools
        )


    # ========================================================
    # 13. FINAL TEXT RESPONSE
    # ========================================================

    reply = response.choices[0].message.content


    # Add the assistant's final response to Gradio history.
    history.append(
        {
            "role": "assistant",
            "content": reply
        }
    )


    # ========================================================
    # 14. GENERATE AUDIO
    # ========================================================

    # voice = talker(reply)


    # ========================================================
    # 15. GENERATE IMAGE IF A CITY WAS USED
    # ========================================================

    image = None

    if cities:

        image = artist(cities[0])


    # ========================================================
    # 16. RETURN EVERYTHING TO GRADIO
    # ========================================================

    return history,  image


# ============================================================
# 17. GRADIO CALLBACK
# ============================================================

def put_message_in_chatbot(message, history):

    return (
        "",
        history + [
            {
                "role": "user",
                "content": message
            }
        ]
    )


# ============================================================
# 18. GRADIO UI
# ============================================================

with gr.Blocks() as ui:

    with gr.Row():

        chatbot = gr.Chatbot(
            height=500
        )

        image_output = gr.Image(
            height=500,
            interactive=False
        )


   
    with gr.Row():

        message = gr.Textbox(
            label="Chat with our AI Assistant:"
        )


    # --------------------------------------------------------
    # User submits a message
    # --------------------------------------------------------

    message.submit(

        put_message_in_chatbot,

        inputs=[
            message,
            chatbot
        ],

        outputs=[
            message,
            chatbot
        ]

    ).then(

        chat,

        inputs=chatbot,

        outputs=[
            chatbot,
        
            image_output
        ]
    )


# ============================================================
# 19. LAUNCH
# ============================================================

ui.launch(
    inbrowser=True,
    share=True
)