import os
import os
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, OpenAIError

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Error: API key is missing!")

else:
    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input="Suggest one simple recipe using eggs and cheese."
        )

        print(response.output_text)

    except AuthenticationError:
        print("Invalid API key. Please check your .env file.")

    except OpenAIError as error:
        print("API error:", error)
