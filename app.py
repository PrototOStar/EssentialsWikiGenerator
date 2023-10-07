from flask import Flask, render_template, request, url_for

app = Flask(__name__)

@app.template_filter('tolist_slice')
def tolist_slice_filter(value, start, end):
    return list(value)[start:end]

# Steal the pokemon from pokemon.txt
pokemon_db = {}

def format_pokemon_data(data):
    return {key: value for key, value in data.items() if key != "Name"}

def parse_evolutions(evolution_str):
    """Parse evolutions from a string and return a list of dictionaries."""
    parts = evolution_str.split(',')
    evolutions = []
    for i in range(0, len(parts), 3):
        evolution_name = parts[i].strip()
        evolution_condition_type = parts[i + 1].strip()
        evolution_condition_value = parts[i + 2].strip()
        
        # Handle empty condition values
        if evolution_condition_value == "":
            evolution_condition_value = None
        
        evolution_data = {
            "name": evolution_name,
            "condition_type": evolution_condition_type,
            "condition_value": evolution_condition_value
        }
        evolutions.append(evolution_data)
        #print(evolutions)
    return evolutions


with open('pokemon.txt', 'r', encoding='utf-8-sig') as file:
    lines = file.readlines()

pokemon_data = {}

for line in lines:
    line = line.strip()

    if line.startswith("["):
        if pokemon_data:
            pokemon_name = pokemon_data["Name"].upper()
            pokemon_db[pokemon_name] = format_pokemon_data(pokemon_data)
            pokemon_data = {}

        pokemon_name = line.strip("[]")
        pokemon_data["Name"] = pokemon_name

    # Convert any strings that should be ints into ints
    elif "=" in line: 
        key, value = line.split("=", 1)
        
        if key.strip() == "BaseStats":
            value = list(map(int, value.split(',')))

        # Convert CatchRate to integer
        if key.strip() == "CatchRate":
            value = int(value)

        if key.strip() == "HatchSteps":
            value = int(value)
        if key.strip() == "Evolutions":
            value = parse_evolutions(value)
        
        pokemon_data[key.strip()] = value

if pokemon_data:
    pokemon_name = pokemon_data["Name"].upper()
    pokemon_db[pokemon_name] = format_pokemon_data(pokemon_data)

# Do typing cringe
def getPokemonResistancesAndWeaknesses(pokemon_types):
    type_chart = {
        "NORMAL": {"weak": [], "resist": [], "immune": ["GHOST"]}, 

        "FIRE": {"weak": ["WATER", "ROCK", "GROUND"], "resist": ["FIRE", "GRASS", "ICE", "BUG", "STEEL", "FAIRY"], "immune": []}, 

        "WATER": {"weak": ["ELECTRIC", "GRASS"], "resist": ["FIRE", "WATER", "ICE", "STEEL"], "immune": []}, 

        "ELECTRIC": {"weak": ["GROUND"], "resist": ["ELECTRIC", "FLYING", "STEEL"], "immune": []}, 

        "GRASS": {"weak": ["FIRE", "ICE", "POISON", "FLYING", "BUG"], "resist": ["WATER", "ELECTRIC", "GRASS", "GROUND"], "immune": []}, 

        "ICE": {"weak": ["FIRE", "FIGHTING", "ROCK", "STEEL"], "resist": ["ICE"], "immune": []}, 

        "FIGHTING": {"weak": ["FLYING", "PSYCHIC", "FAIRY"], "resist": ["BUG", "ROCK", "DARK"], "immune": []}, 

        "POISON": {"weak": ["GROUND", "PSYCHIC"], "resist": ["GRASS", "FIGHTING", "POISON", "BUG", "FAIRY"], "immune": []}, 

        "GROUND": {"weak": ["WATER", "ICE", "GRASS"], "resist": ["POISON", "ROCK"], "immune": ["ELECTRIC"]}, 

        "FLYING": {"weak": ["ELECTRIC", "ICE", "ROCK"], "resist": ["GRASS", "FIGHTING", "BUG"], "immune": ["GROUND"]}, 

        "PSYCHIC": {"weak": ["BUG", "GHOST", "DARK"], "resist": ["FIGHTING", "PSYCHIC"], "immune": []}, 

        "BUG": {"weak": ["FIRE", "FLYING", "ROCK"], "resist": ["GRASS", "FIGHTING", "GROUND"], "immune": []}, 

        "ROCK": {"weak": ["WATER", "GRASS", "FIGHTING", "GROUND", "STEEL"], "resist": ["NORMAL", "FIRE", "POISON", "FLYING"], "immune": []}, 

        "GHOST": {"weak": ["GHOST", "DARK"], "resist": ["POISON", "BUG"], "immune": ["NORMAL", "FIGHTING"]}, 

        "DRAGON": {"weak": ["ICE", "DRAGON", "FAIRY"], "resist": ["FIRE", "WATER", "ELECTRIC", "GRASS"], "immune": []}, 

        "DARK": {"weak": ["FIGHTING", "BUG", "FAIRY"], "resist": ["GHOST", "DARK"], "immune": ["PSYCHIC"]}, 

        "STEEL": {"weak": ["FIRE", "FIGHTING", "GROUND"], "resist": ["NORMAL", "GRASS", "ICE", "FLYING", "PSYCHIC", "BUG", "ROCK", "DRAGON", "STEEL", "FAIRY"], "immune": ["POISON"]}, 

        "FAIRY": {"weak": ["POISON", "STEEL"], "resist": ["FIGHTING", "BUG", "DARK"], "immune": ["DRAGON"]} 
    } 
 
    
    effectiveness = {type_name: 1 for type_name in type_chart.keys()}
    
    for poke_type in pokemon_types:
        for type_name in type_chart.keys():
            if type_name in type_chart[poke_type]["weak"]:
                effectiveness[type_name] *= 2
            elif type_name in type_chart[poke_type]["resist"]:
                effectiveness[type_name] *= 0.5
            elif type_name in type_chart[poke_type]["immune"]:
                effectiveness[type_name] *= 0
    
    return effectiveness

# WebPages / HTML
@app.route('/')
def index():
    return render_template("index.html", pokemon_db=pokemon_db)

@app.route('/pokemon/<name>')
def pokemon(name):
    name = name.upper()
    data = pokemon_db.get(name, {})
    print(data)
    if not data:
        return "Pokemon not found", 404

    # Get its types and weaknesses
    types = data.get("Types", "").strip().split(",")
    effectiveness = getPokemonResistancesAndWeaknesses(types)
    
    # Get its evolutions
    evolutions = []
    for evolution_data in data.get("Evolutions", []):
        evolution_name = evolution_data.get("Name")
        if evolution_name:
            evolution = pokemon_db.get(evolution_name.upper(), {})
            evolutions.append(evolution)
    print(evolutions)

    return render_template("pokemon.html", name=name, data=data, effectiveness=effectiveness, db=pokemon_db)

@app.route('/search', methods=['POST'])
def search():
    name = request.form.get('name').lower()
    matches = [poke for poke in pokemon_db if name in poke.lower()][:10]

    if len(matches) == 1:
        return redirect(url_for('pokemon', name=matches[0].upper()))
    return render_template('search_results.html', matches=matches)


if __name__ == '__main__':
    app.run(debug=True)
