import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_questions(topic: str):
    try:
        response = openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a quiz question generator."},
                {"role": "user", "content": f"Generate 5 multiple-choice questions on the topic: {topic}."},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}
