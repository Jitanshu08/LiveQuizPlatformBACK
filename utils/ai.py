import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_questions(topic: str):
    try:
        # Await the coroutine correctly
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a quiz question generator."},
                {"role": "user", "content": f"Generate 5 multiple-choice questions on the topic: {topic}."},
            ],
        )
        # Access the response content properly
        return response.choices[0].message["content"]
    except Exception as e:
        # Handle exceptions and return error messages
        return {"error": str(e)}
