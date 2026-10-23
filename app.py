import json
import streamlit as st

from main import generate_recipes


# ----------------------------------------
# 1. Page settings
# ----------------------------------------

st.set_page_config(
    page_title="The Recipe Studio",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ----------------------------------------
# 2. Custom styling
# ----------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');

:root {
    --cream: #FAF8F3;
    --green: #3E604B;
    --dark: #24352B;
    --muted: #788078;
    --border: #E8E9E1;
}

.stApp {
    background-color: var(--cream);
    color: var(--dark);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

h1, h2, h3 {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: var(--dark) !important;
    letter-spacing: -0.5px;
}

h1 {
    font-size: 3.7rem !important;
    line-height: 1.15 !important;
}

h2 {
    font-size: 2rem !important;
}

p, label {
    color: var(--dark);
}

.hero-kicker {
    color: var(--green);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 15px;
}

.hero-description {
    color: #68766A;
    font-size: 1.08rem;
    line-height: 1.8;
    max-width: 550px;
}

.section-kicker {
    color: var(--green);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.small-note {
    color: #849085;
    font-size: 0.85rem;
}

.recipe-number {
    color: var(--green);
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.recipe-meta {
    color: #758075;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.stButton > button[kind="primary"] {
    background-color: var(--green);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.85rem 2rem;
    font-weight: 700;
    min-height: 52px;
}

.stButton > button[kind="primary"]:hover {
    background-color: #294534;
    color: white;
    border: none;
}

.stTextInput input,
.stNumberInput input {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px;
}

hr {
    border-color: var(--border);
}

footer {
    visibility: hidden;
}

@media (max-width: 768px) {
    h1 {
        font-size: 2.6rem !important;
    }

    .block-container {
        padding-top: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------
# 3. Decorative food photographs
# ----------------------------------------

HERO_IMAGE = (
    "https://images.unsplash.com/"
    "photo-1547592180-85f173990554"
    "?auto=format&fit=crop&w=1200&q=85"
)

RECIPE_IMAGES = [
    (
        "https://images.unsplash.com/"
        "photo-1473093295043-cdd812d0e601"
        "?auto=format&fit=crop&w=900&q=85"
    ),
    (
        "https://images.unsplash.com/"
        "photo-1512621776951-a57141f2eefd"
        "?auto=format&fit=crop&w=900&q=85"
    ),
    (
        "https://images.unsplash.com/"
        "photo-1546069901-ba9599a7e63c"
        "?auto=format&fit=crop&w=900&q=85"
    )
]


# ----------------------------------------
# 4. Build the OpenAI prompt
# ----------------------------------------

def build_prompt(preferences):
    return f"""
You are a helpful and creative cooking assistant.

User preferences:
{json.dumps(preferences)}

Return exactly 3 different recipes as a JSON object.

The JSON object must have a key called "recipes"
containing a list of exactly 3 recipe objects.

Each recipe must contain:
- "title": a descriptive recipe name (string)
- "cook_time": total cooking time in minutes (integer)
- "ingredients": a list of ingredient objects
- "instructions": a list of cooking steps (strings)

Each ingredient object must contain:
- "name": ingredient name (string)
- "quantity": quantity needed (string)
- "missing": boolean (true or false)

Mark an ingredient as missing if it is not
in the user's available ingredients.

Treat equivalent names such as "egg" and "eggs"
as the same ingredient.

Do not assume the user has oil, salt, spices,
or other pantry ingredients unless listed.

Include every ingredient required to make
each recipe, including missing ingredients.

Respect dietary restrictions, cuisine,
maximum cooking time, and servings if provided.

If a maximum cooking time is given, each recipe
must fit within that limit.

Make instructions clear and easy to follow.

Return only valid JSON.
"""


# ----------------------------------------
# 5. Header
# ----------------------------------------

st.markdown(
    '<div class="hero-kicker">YOUR PERSONAL AI CHEF</div>',
    unsafe_allow_html=True
)

hero_left, hero_right = st.columns(
    [1.2, 1],
    gap="large",
    vertical_alignment="center"
)

with hero_left:
    st.title("Good food starts with what you have.")

    st.markdown(
        """
        <p class="hero-description">
        Turn everyday ingredients into something wonderful.
        Tell us what's in your kitchen, and discover three
        delicious recipes made just for you.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="small-note">✦ Thoughtful recipes · Less food waste · More inspiration</p>',
        unsafe_allow_html=True
    )

with hero_right:
    st.image(HERO_IMAGE, use_container_width=True)


st.write("")
st.write("")
st.divider()


# ----------------------------------------
# 6. Recipe preferences form
# ----------------------------------------

st.markdown(
    '<div class="section-kicker">LET’S GET COOKING</div>',
    unsafe_allow_html=True
)

st.header("What's in your kitchen?")

st.write(
    "Share your ingredients and preferences. "
    "We'll take care of the inspiration."
)

with st.form("recipe_form"):
    ingredients = st.text_input(
        "Available ingredients",
        placeholder="e.g. eggs, tomatoes, cheese, spinach",
        help="Separate ingredients with commas."
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        dietary = st.text_input(
            "Dietary preferences",
            placeholder="e.g. vegetarian, gluten-free"
        )

        max_time = st.number_input(
            "Maximum cooking time (minutes)",
            min_value=0,
            value=0,
            step=5,
            help="Leave at 0 for no time limit."
        )

    with col2:
        cuisine = st.text_input(
            "Favorite cuisine",
            placeholder="e.g. Italian, Mediterranean"
        )

        servings = st.number_input(
            "Number of servings",
            min_value=0,
            value=0,
            step=1,
            help="Leave at 0 if you have no preference."
        )

    st.write("")

    submitted = st.form_submit_button(
        "✦ Discover my recipes",
        type="primary",
        use_container_width=True
    )


# ----------------------------------------
# 7. Generate recipes
# ----------------------------------------

if submitted:
    ingredient_list = [
        item.strip()
        for item in ingredients.split(",")
        if item.strip()
    ]

    if not ingredient_list:
        st.error(
            "Please enter at least one ingredient "
            "to get started."
        )

    else:
        preferences = {
            "ingredients": ingredient_list,
            "dietary": dietary.strip() or None,
            "cuisine": cuisine.strip() or None,
            "max_cook_time": int(max_time) or None,
            "servings": int(servings) or None
        }

        prompt = build_prompt(preferences)

        with st.spinner(
            "Our AI chef is creating your recipes..."
        ):
            recipes = generate_recipes(
                prompt,
                max_time=preferences["max_cook_time"]
            )

        if recipes:
            st.session_state["recipes"] = recipes
        else:
            st.session_state.pop("recipes", None)
            st.error(
                "We couldn't create your recipes this time. "
                "Please try again."
            )


# ----------------------------------------
# 8. Display beautiful recipe cards
# ----------------------------------------

recipes = st.session_state.get("recipes")

if recipes:
    st.write("")
    st.write("")
    st.divider()

    st.markdown(
        '<div class="section-kicker">MADE JUST FOR YOU</div>',
        unsafe_allow_html=True
    )

    st.header("Your recipe collection")

    st.write(
        "Three delicious possibilities, "
        "inspired by the ingredients you have."
    )

    st.write("")

    for index, recipe in enumerate(recipes):
        with st.container(border=True):
            image_col, content_col = st.columns(
                [1, 1.4],
                gap="large"
            )

            with image_col:
                st.image(
                    RECIPE_IMAGES[index % len(RECIPE_IMAGES)],
                    use_container_width=True
                )

                st.caption(
                    "Illustrative food photography"
                )

            with content_col:
                st.markdown(
                    f'<div class="recipe-number">'
                    f'RECIPE {index + 1:02d}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.subheader(recipe["title"])

                st.markdown(
                    f'<div class="recipe-meta">'
                    f'⏱ {recipe["cook_time"]} minutes'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.markdown("**What you'll need**")

                for ingredient in recipe["ingredients"]:
                    name = ingredient["name"]
                    quantity = ingredient["quantity"]

                    if ingredient["missing"]:
                        st.write(
                            f"🛒 **Need to buy:** "
                            f"{name} — {quantity}"
                        )
                    else:
                        st.write(
                            f"🌿 **Already have:** "
                            f"{name} — {quantity}"
                        )

            st.divider()

            st.markdown("**Let's make it**")

            for step_number, instruction in enumerate(
                recipe["instructions"],
                start=1
            ):
                st.write(
                    f"**{step_number}.** {instruction}"
                )

        st.write("")


# ----------------------------------------
# 9. Footer
# ----------------------------------------

st.write("")
st.divider()

st.markdown(
    """
    <p style="
        text-align:center;
        color:#879087;
        font-size:0.85rem;
        padding:20px 0;
    ">
        🌿 THE RECIPE STUDIO
        <br>
        Made with Python, Streamlit & OpenAI
    </p>
    """,
    unsafe_allow_html=True
)
