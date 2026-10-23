import os
import json
import time

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
    AuthenticationError,
    OpenAIError
)


# ----------------------------------------
# 1. Load the OpenAI API key
# ----------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "API key is missing! Check your .env file."
    )

# Disable automatic retries because we
# implement our own retry logic below.
client = OpenAI(
    api_key=api_key,
    max_retries=0
)


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

        if (
            max_time is not None
            and recipe["cook_time"] > max_time
        ):
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

            name = ingredient.get("name")
            quantity = ingredient.get("quantity")
            missing = ingredient.get("missing")

            if not isinstance(name, str) or not name.strip():
                return False

            if (
                not isinstance(quantity, str)
                or not quantity.strip()
            ):
                return False

            if type(missing) is not bool:
                return False

        for instruction in recipe["instructions"]:
            if (
                not isinstance(instruction, str)
                or not instruction.strip()
            ):
                return False

    return True


def generate_recipes(prompt, max_time=None):
    for attempt in range(2):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                text={
                    "format": {
                        "type": "json_object"
                    }
             },
                timeout=30,
                max_output_tokens=4000
            )

            try:
                data = json.loads(response.output_text)

            except json.JSONDecodeError:
                print("Error: AI returned invalid JSON.")
                return None

            if not isinstance(data, dict):
                print("Error: Expected a JSON object.")
                return None

            recipes = data.get("recipes")

            if not validate_recipes(recipes, max_time):
                print(
                    "Error: AI returned invalid recipe data."
                )
                return None

            return recipes

        except (
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
            InternalServerError
        ) as error:

            print(
                "Temporary API error:",
                type(error).__name__
            )

            if attempt == 0:
                print(
                    "Waiting 2 seconds before retrying..."
                )
                time.sleep(2)

            else:
                print("Both attempts failed.")
                return None

        except AuthenticationError:
            print(
                "Invalid API key. Check your .env file."
            )
            return None

        except OpenAIError as error:
            print("API error:", error)
            return None

    return None

def display_recipes(recipes):
    for number, recipe in enumerate(recipes, start=1):
        print("\n" + "=" * 40)
        print(f"RECIPE {number}: {recipe['title']}")
        print("=" * 40)

        print(
            f"Cooking time: {recipe['cook_time']} minutes"
        )

        print("\nIngredients:")

        for ingredient in recipe["ingredients"]:
            name = ingredient["name"]
            quantity = ingredient["quantity"]
            missing = ingredient["missing"]

            if missing:
                print(
                    f"[MISSING] {name} - {quantity}"
                )
            else:
                print(
                    f"[HAVE] {name} - {quantity}"
                )

        print("\nInstructions:")

        for step_number, instruction in enumerate(
            recipe["instructions"],
            start=1
        ):
            print(f"{step_number}. {instruction}")

    print("\nEnjoy your meals!")


def main():
    print("Welcome to AI Recipe Generator!")

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

    dietary = input(
        "Dietary restrictions (optional): "
    ).strip()

    cuisine = input(
        "Preferred cuisine (optional): "
    ).strip()

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

The JSON object must contain a key called
"recipes" with a list of exactly 3 recipes.

Each recipe must contain:
- "title": recipe name (string)
- "cook_time": estimated total cooking minutes (integer)
- "ingredients": list of ingredient objects
- "instructions": list of cooking steps (strings)

Each ingredient object must contain:
- "name": ingredient name (string)
- "quantity": amount needed (string)
- "missing": true or false (boolean)

Mark an ingredient as missing if it is not
in the user's available ingredient list.

Treat similar ingredient names as equivalent,
such as "egg" and "eggs".

Do not assume the user has oil, salt, spices,
or other pantry items unless they listed them.

Include all ingredients needed for each recipe,
including any ingredients the user must buy.

Respect dietary restrictions and cuisine
preferences when provided.

If a maximum cooking time is provided,
every recipe must fit within that limit.

If servings are provided, adjust ingredient
quantities accordingly.

Return only valid JSON.
"""

    print("\nGenerating your recipes...\n")

    recipes = generate_recipes(
        prompt,
        max_time=max_time
    )

    if recipes:
        display_recipes(recipes)
    else:
        print("Sorry, recipes could not be generated.")


if __name__ == "__main__":
    main()
