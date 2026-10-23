# AI Recipe Generator

A Python command-line application that uses the OpenAI API to generate three recipes based on ingredients provided by the user.

## Features

- Accepts a list of available ingredients.
- Supports optional dietary restrictions and cuisine preferences.
- Supports maximum cooking time and number of servings.
- Generates exactly three recipe suggestions.
- Displays recipe titles, ingredients, quantities, cooking instructions, and estimated cooking times.
- Marks ingredients as `[HAVE]` or `[MISSING]`.
- Validates the structure of the AI-generated recipes.
- Handles API errors and retries temporary failures.

## Requirements

- Python 3.10 or newer
- An OpenAI API key
- Internet connection

## Installation

1. Clone the repository and open its folder:

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd AI_Recipe_Generator
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Activate the environment on macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project folder:

   ```text
   OPENAI_API_KEY=your_actual_api_key
   ```

   Never commit your real API key to GitHub.

## Usage

Run the application:

```bash
python main.py
```

Enter your ingredients and optional preferences when prompted.

## Example Invocation

```text
Welcome to AI Recipe Generator!

Enter your ingredients (separated by commas): eggs, cheese, tomatoes
Dietary restrictions (optional): vegetarian
Preferred cuisine (optional): Italian
Maximum cooking time in minutes (optional): 20
Number of servings (optional): 2

Generating your recipes...
```

## Example Output (Illustrative)

```text
Recipe 1: Tomato and Cheese Omelette
Cooking time: 15 minutes

Ingredients:
[HAVE] Eggs - 3
[HAVE] Cheese - 50 g
[HAVE] Tomatoes - 2
[MISSING] Olive oil - 1 tablespoon

Instructions:
1. Beat the eggs in a bowl.
2. Chop the tomatoes.
3. Heat olive oil in a pan.
4. Add eggs, tomatoes, and cheese.
5. Cook until set.
```

The application generates three recipes. Actual results vary depending on the ingredients and AI response.

## Error Handling

The application validates user input, checks the structure of the returned recipes, handles API errors, and retries temporary API failures once.

## Technologies

- Python
- OpenAI API
- python-dotenv
- JSON
