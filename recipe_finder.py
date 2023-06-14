import io
import PySimpleGUI as psg
import requests
import os
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


def get_api_key():
    """ Get the api key from api_key.txt file."""
    with open('keys/api_key.txt') as api_file:
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
            ingredients.append([name, amount, unit])
        return ingredients
    else:
        print("Error: Unable to fetch recipe details.")


def create_thumbnail(image_url):
    """Create thumbnail from the URL fetched from API."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with Image.open(BytesIO(response.content)) as image:
            image.thumbnail((156, 116))

            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save("thumb.png", 'PNG')

    except (requests.HTTPError, IOError) as e:
        print(f"Unable to resize image from {image_url}: {e}")


def save_to_file(filename, title, information, ingredients):
    """Save recipe to a txt file."""
    with open(filename + ".txt", 'w') as file:
        file.write(title + '\n\n')
        for ingredient in ingredients:
            ingredient_str = [str(item) for item in ingredient]
            file.write(', '.join(ingredient_str) + '\n')
        file.write('\n' + information + '\n')


def delete_file(file_path):
    """Delete file for a given path."""
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error occurred while deleting file {file_path}: {e}")


def create_window():
    """Layout for a main window."""
    layout = [
        [
            psg.Column(
                [
                    [psg.VPush()],
                    [psg.Text("RECIPE FINDER")],
                    [psg.Input(key="-SEARCH-TERM-", size=28), psg.Button("Search", key="-SEARCH-")],
                    [psg.Listbox(values=[], size=(35, 15), key="-LISTBOX-")],
                    [psg.Button("Save txt", key="-SAVE-"), psg.Push(), psg.Button("Show", key="-SUBMIT-")]
                ],
                element_justification='center', size=(300, 400)
            ),
            psg.Column(
                [
                    [psg.VPush()],
                    [psg.Image(filename="images/dummy.png", key="-THUMBNAIL-")],
                    [psg.Listbox(values=[], size=(45, 5), font="Arial 8", key="-INGREDIENTS-")],
                    [psg.Multiline(size=(38, 9), key="-INFO-")]
                ],
                element_justification='center', size=(300, 400)
            )
        ]
    ]
    return psg.Window("Recipe Finder", layout,
                      size=(640, 400),
                      resizable=True,
                      element_justification="center")


def main():
    """Main function with all the logic."""
    chosen_recipe_name = []
    information = ""
    ingredients = []
    recipe_id = []
    recipe_names = []
    recipe_photo = []

    key = get_api_key()
    window = create_window()

    while True:
        event, values = window.read()
        if event == psg.WINDOW_CLOSED:
            break

        if event == "-SEARCH-":
            search_term = values["-SEARCH-TERM-"]
            try:
                results = search_recipes(search_term, key)
            except requests.exceptions.ConnectionError:
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

            create_thumbnail(chosen_recipe_photo)
            ingredients = get_recipe_ingredients(chosen_recipe_id, key)
            information = get_recipe_information(chosen_recipe_id, key)

            window["-INGREDIENTS-"].update(ingredients)
            window["-INFO-"].update(information[1])
            window["-THUMBNAIL-"].update("thumb.png")
            delete_file("thumb.png")

        if event == "-SAVE-":
            folder = psg.PopupGetFolder(message="Where do you want to save the file?")
            filename = psg.popup_get_text(message="filename")
            save_to_file(os.path.join(folder, filename), chosen_recipe_name[0], information[1], ingredients)

    window.close()
    exit(0)


if __name__ == "__main__":
    main()
