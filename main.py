import time
import json

from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
    AuthenticationError,
    OpenAIError
)
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import time


def generate_recipes(prompt):
    for attempt in range(2):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                timeout=30,
                max_output_tokens=3000
            )

            try:
                data = json.loads(response.output_text)

                if not isinstance(data, dict):
                    print("Error: Expected a JSON object.")
                    return None

                recipes = data.get("recipes")

                if not validate_recipes(recipes, preferences["max_cook_time"]):
                    print("Error: AI returned invalid recipe data.")
                    return None

                return recipes

            except json.JSONDecodeError:
                print("Error: AI returned invalid JSON.")
                return None

        except (
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
            InternalServerError
        ) as error:

            print("Temporary API error:", type(error).__name__)

            if attempt == 0:
                print("Waiting 2 seconds before retrying...")
                time.sleep(2)
            else:
                print("Both attempts failed.")
                return None

        except AuthenticationError:
            print("Invalid API key. Check your .env file.")
            return None

        except OpenAIError as error:
            print("API error:", error)
            return None


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key is missing!")

client = OpenAI(api_key=api_key)


def get_positive_number(question):
    while True:
        value = input(question).strip()

        if value == "":
            return None

        try:
            number = int(value)

            if number > 0:
                return number

            print("Please enter a positive number.")

        except ValueError:
            print("Please enter a valid number.")


print("Welcome to AI Recipe Generator!")

def validate_recipes(recipes, max_time=None):
    if not isinstance(recipes, list):
        return False

    if len(recipes) != 3:
        return False

    for recipe in recipes:
        if not isinstance(recipe, dict):
            return False

        required_keys = [
            "title",
            "cook_time",
            "ingredients",
            "instructions"
        ]

        for key in required_keys:
            if key not in recipe:
                return False

        if not isinstance(recipe["title"], str):
            return False

        if not recipe["title"].strip():
            return False

        if type(recipe["cook_time"]) is not int:
            return False

        if recipe["cook_time"] <= 0:
            return False
        if max_time is not None and recipe["cook_time"] > max_time:
            return False

        if not isinstance(recipe["ingredients"], list):
            return False

        if not recipe["ingredients"]:
            return False

        if not isinstance(recipe["instructions"], list):
            return False

        if not recipe["instructions"]:
            return False

        for ingredient in recipe["ingredients"]:
            if not isinstance(ingredient, dict):
                return False

            if not isinstance(ingredient.get("name"), str):
                return False

            if not ingredient["name"].strip():
                return False

            if not isinstance(ingredient.get("quantity"), str):
                return False

            if not ingredient["quantity"].strip():
                return False

            if type(ingredient.get("missing")) is not bool:
                return False

        for instruction in recipe["instructions"]:
            if not isinstance(instruction, str):
                return False

            if not instruction.strip():
                return False

    return True


def display_recipes(recipes):
    if len(recipes) != 3:
        print("Error: Expected exactly 3 recipes.")
        return

    for number, recipe in enumerate(recipes, start=1):
        print(f"\nRecipe {number}: {recipe['title']}")
        print(f"Cooking time: {recipe['cook_time']} minutes")

        print("\nIngredients:")

        for ingredient in recipe["ingredients"]:
            name = ingredient["name"]
            quantity = ingredient["quantity"]
            missing = ingredient["missing"]

            if missing:
                print(f"[MISSING] {name} - {quantity}")
            else:
                print(f"[HAVE] {name} - {quantity}")

        print("\nInstructions:")

        for step_number, instruction in enumerate(
            recipe["instructions"], start=1
        ):
            print(f"{step_number}. {instruction}")


while True:
    ingredients = input(
        "Enter your ingredients (separated by commas): "
    )

    ingredient_list = [
        item.strip()
        for item in ingredients.split(",")
        if item.strip()
    ]

    if ingredient_list:
        break

    print("Please enter at least one ingredient.")

dietary = input("Dietary restrictions (optional): ").strip()
cuisine = input("Preferred cuisine (optional): ").strip()

max_time = get_positive_number(
    "Maximum cooking time in minutes (optional): "
)

servings = get_positive_number(
    "Number of servings (optional): "
)

preferences = {
    "ingredients": ingredient_list,
    "dietary": dietary or None,
    "cuisine": cuisine or None,
    "max_cook_time": max_time,
    "servings": servings
}


prompt = f"""
You are a helpful cooking assistant.

User preferences:
{json.dumps(preferences)}

Return exactly 3 recipes as a JSON object.

The JSON object must contain a key called "recipes"
with a list of exactly 3 recipes.

Each recipe must contain:
- "title": recipe name (string)
- "cook_time": estimated minutes (integer)
- "ingredients": list of ingredient objects
- "instructions": list of cooking steps (strings)

Each ingredient object must contain:
- "name": ingredient name
- "quantity": amount needed
- "missing": true if not in user's ingredients,
             otherwise false

Respect the user's dietary restrictions, cuisine,
maximum cooking time, and servings when provided.

Include all ingredients required for each recipe.
Return only valid JSON.
"""


print("\nGenerating your recipes...\n")


print("\nGenerating your recipes...\n")


recipes = generate_recipes(prompt)

if recipes:
    display_recipes(recipes)
else:
    print("Sorry, recipes could not be generated.")
