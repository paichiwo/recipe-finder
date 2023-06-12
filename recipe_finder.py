import requests
from bs4 import BeautifulSoup
import PySimpleGUI as psg


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
        'number': 20
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        recipe_results = response.json()['results']

        for recipe in recipe_results:
            recipe_id = recipe['id']
            recipe_title = recipe['title']
            recipe_image = recipe['image']
            recipes.append((recipe_id, recipe_title, recipe_image))
        return recipes
    else:
        print("Error: Unable to fetch recipe details.")


def get_recipe_information(recipe_id, api_key):
    """Fetch the detailed recipe information."""

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
        return ingredients
    else:
        print("Error: Unable to fetch recipe details.")


def layouts():

    layout = [
        [psg.Image(filename="Layer 1.png"), psg.Listbox(values=[], size=(30, 6), expand_x=True, font="Arial 8", key="-INGREDIENTS-")],
        [psg.Multiline(size=(30, 5), expand_x=True, key="-INFO-")],
        [psg.VPush()],
        [psg.Text("Recipe Finder")],
        [psg.Input(key="-SEARCH-TERM-")],
        [psg.Button("Search", key="-SEARCH-"), psg.Button("Submit", key="-SUBMIT-", disabled=True)],
        [psg.Listbox(values=[], size=(40, 10), expand_x=True, key="-LISTBOX-")]
    ]

    return psg.Window("Recipe Finder", layout, size=(500, 600), element_justification="center")


def main_window():

    recipe_id = []
    recipe_names = []
    recipe_photo = []

    key = get_api_key()

    window = layouts()

    while True:
        event, values = window.read()
        if event == psg.WINDOW_CLOSED:
            break

        if event == "-SEARCH-":
            search_term = values["-SEARCH-TERM-"]
            results = search_recipes(search_term, key)

            recipe_id = [recipe[0] for recipe in results]
            recipe_names = [recipe[1] for recipe in results]
            recipe_photo = [recipe[2] for recipe in results]

            window["-LISTBOX-"].update(values=recipe_names)
            window["-SUBMIT-"].update(disabled=False)

        if event == "-SUBMIT-":
            chosen_recipe_name = values["-LISTBOX-"]
            chosen_recipe_index = recipe_names.index(chosen_recipe_name[0])

            chosen_recipe_id = recipe_id[chosen_recipe_index]
            chosen_recipe_photo = recipe_photo[chosen_recipe_index]

            ingredients = get_recipe_ingredients(chosen_recipe_id, key)
            information = get_recipe_information(chosen_recipe_id, key)
            print(information)
            print(chosen_recipe_photo)

            window["-INGREDIENTS-"].update(ingredients)
            window["-INFO-"].update(information[1])
    window.close()
    exit(0)


if __name__ == "__main__":
    main_window()
