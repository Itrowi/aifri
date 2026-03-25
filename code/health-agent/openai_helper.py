import os
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

async def get_simple_explanation(text: str) -> str:
    # Uses OpenAI's GPT-3.5/4 to simplify the text
    prompt = (
        "Explain the following medical abstract in the simplest way possible, "
        "as if talking to a 10-year-old. Use short sentences. Avoid medical jargon. "
        "If the text is not in English, translate and simplify it.\n\n" + text
    )
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()
