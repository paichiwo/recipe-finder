import requests
from bs4 import BeautifulSoup
from tkinter import *
from PIL import Image


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


def main():
    key = get_api_key()
    search_term = input("Search: ")
    print(search_recipes(search_term, key))
    recipe_id = input("Enter id: ")
    print(get_recipe_ingredients(recipe_id, key))
    title, info = get_recipe_information(recipe_id, key)
    print(title, "\n", info)


root = Tk()
root.title('Recipe App')
root.geometry("700x655")
root.config(bg='black')

background_main_window = PhotoImage(file='RecipeFinder.png')
background_main_window_label = Label(image=background_main_window)
background_main_window_label.place(x=0, y=0)

search_button_image = PhotoImage(file='search.png')
search_button = Button(image=search_button_image, bg='white', borderwidth=0, activebackground='white', command=main)
search_button.place(x=490, y=118)

search_bar = Entry(font=("Noto Sans", 15), bg='white', width=24, borderwidth=0)
search_bar.place(x=220, y=118)

root.mainloop()

