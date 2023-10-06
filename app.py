from flask import Flask, render_template_string, request

app = Flask(__name__)

# Dictionary to store Pokémon data
pokemon_db = {}

def format_pokemon_data(data):
    return {key: value for key, value in data.items() if key != "Name"}

with open('pokemon.txt', 'r', encoding='utf-8-sig') as file:
    lines = file.readlines()

pokemon_data = {}

for line in lines:
    line = line.strip()

    if line.startswith("["):
        if pokemon_data:
            pokemon_name = pokemon_data["Name"]
            pokemon_db[pokemon_name] = format_pokemon_data(pokemon_data)
            pokemon_data = {}

        pokemon_name = line.strip("[]")
        pokemon_data["Name"] = pokemon_name

    elif "=" in line:
        key, value = line.split("=", 1)
        pokemon_data[key.strip()] = value.strip()

if pokemon_data:
    pokemon_name = pokemon_data["Name"]
    pokemon_db[pokemon_name] = format_pokemon_data(pokemon_data)

@app.route('/')
def index():
    return render_template_string("""
        <form action="/search" method="post">
            Search: <input type="text" id="searchInput" onkeyup="filterFunction()" name="name">
            <input type="submit" value="Search">
        </form>
        <ul id="pokemonList">
        {% for name in pokemon_db.keys() %}
            <li><a href="/pokemon/{{ name }}">{{ name }}</a></li>
        {% endfor %}
        </ul>
        <script>
        function filterFunction() {
            var input, filter, ul, li, a, i;
            input = document.getElementById('searchInput');
            filter = input.value.toLowerCase().replace(/ /g, '');
            ul = document.getElementById("pokemonList");
            li = ul.getElementsByTagName('li');
            for (i = 0; i < li.length; i++) {
                a = li[i].getElementsByTagName("a")[0];
                if (a.innerHTML.toLowerCase().replace(/ /g, '').includes(filter)) {
                    li[i].style.display = "";
                } else {
                    li[i].style.display = "none";
                }
            }
        }
        </script>
    """, pokemon_db=pokemon_db)

@app.route('/pokemon/<name>')
def pokemon(name):
    data = pokemon_db.get(name, {})
    return render_template_string("""
        <h1>{{ name }}</h1>
        <ul>
        {% for key, value in data.items() %}
            <li><strong>{{ key }}</strong>: {{ value }}</li>
        {% endfor %}
        </ul>
        <a href="/">Back</a>
    """, name=name, data=data)

@app.route('/search', methods=['POST'])
def search():
    name = request.form.get('name')
    if name in pokemon_db:
        return pokemon(name)
    else:
        return "Pokémon not found."

if __name__ == '__main__':
    app.run(debug=True)
