
import os
import json
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("SPOONACULAR_API_KEY")

app = Flask(__name__)

def load_fallback():
    """Load recipes from fallback.json if API fails"""
    with open("fallback.json", "r") as f:
        data = json.load(f)
        return data.get("recipes", [])

@app.route("/", methods=["GET", "POST"])
def index():
    recipes = []
    error = None

    if request.method == "POST":
        ingredients = request.form.get("ingredients", "").strip()
        if not ingredients:
            error = " Please enter ingredients."
        elif not API_KEY:
            error = " API key not found. Please add it in your .env file."
        else:
            url = "https://api.spoonacular.com/recipes/complexSearch"
            params = {
                "apiKey": API_KEY,
                "query": ingredients,
                "number": 3,
                "addRecipeInformation": True,
                "addRecipeNutrition": True
            }
            try:
                response = requests.get(url, params=params, timeout=6)  # timeout after 6 sec
                response.raise_for_status()
                data = response.json()

                recipes = []
                for rec in data.get("results", []):
                    # Extract nutrients
                    nutrients = rec.get("nutrition", {}).get("nutrients", [])
                    def get_nutrient(name):
                        for n in nutrients:
                            if n.get("name", "").lower() == name.lower():
                                return f"{n['amount']} {n['unit']}"
                        return "N/A"

                    recipes.append({
                        "title": rec.get("title"),
                        "image": rec.get("image"),
                        "link": rec.get("sourceUrl"),
                        "calories": get_nutrient("Calories"),
                        "protein": get_nutrient("Protein"),
                        "carbs": get_nutrient("Carbohydrates"),
                        "fat": get_nutrient("Fat"),
                    })

            except Exception as e:
                print(" API failed, loading fallback:", e)
                recipes = load_fallback()   # load local JSON data instead
                error = " API is slow/unavailable. Showing fallback recipes."

    return render_template("index.html", recipes=recipes, error=error)

if __name__ == "__main__":
    app.run(debug=True)
