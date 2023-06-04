import requests
from bs4 import BeautifulSoup


def get_api_key():
    """ Get the api key from api_key.txt file."""
    with open('api_key.txt') as api_file:
        api_key = api_file.read()
    return api_key


def search_recipes(search_term, api_key):
    """Search for recipes using keyword."""

    recipes = []
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'apiKey': api_key,
        'query': search_term,
        'number': 10
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        recipe_results = response.json()['results']

        for recipe in recipe_results:
            recipe_id = recipe['id']
            recipe_title = recipe['title']
            recipe_image = recipe['image']
            recipes.append((recipe_id, recipe_title, recipe_image))
    print(recipes)
    return recipes


def get_recipe_information(recipe_id, api_key):
    """Fetch the detailed recipe information."""

    recipe_information = []
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {
        'apiKey': api_key,
        'includeNutrition': True  # Set to True if you want nutrition information included
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        recipe_details = response.json()

        recipe_title = recipe_details['title']
        recipe_instructions = recipe_details['instructions']

        soup = BeautifulSoup(recipe_instructions, 'html.parser')
        recipe_instructions_text = soup.get_text()
        return recipe_title, recipe_instructions_text
        # recipe_information.append((recipe_title, recipe_instructions_text))
    else:
        print("Error: Unable to fetch recipe details.")


def get_recipe_ingredients(recipe_id, api_key):
    """Fetch the ingredients for a given recipe ID."""

    ingredients = []
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/ingredientWidget.json'
    params = {
        'apiKey': api_key,
        'metric': 'true'  # Added metric parameter
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        ingredient_data = response.json()['ingredients']

        for ingredient in ingredient_data:
            name = ingredient['name']
            amount = ingredient['amount']['metric']['value']
            unit = ingredient['amount']['metric']['unit']

            ingredients.append((name, amount, unit))
        print(ingredients)
        return ingredients
    else:
        return []


def main():
    key = get_api_key()
    search_term = input("Search: ")
    search_recipes(search_term, key)
    recipe_id = input("Enter id: ")
    get_recipe_ingredients(recipe_id, key)
    title, info = get_recipe_information(recipe_id, key)
    print(title, "\n", info)


if __name__ == "__main__":
    main()
