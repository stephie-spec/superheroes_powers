from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///superheroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return '<h1>Superheroes API</h1>'

# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    heroes_data = []
    for hero in heroes:
        heroes_data.append({
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        })
    return jsonify(heroes_data)

# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    
    hero_powers_data = []
    for hero_power in hero.hero_powers:
        hero_powers_data.append({
            "id": hero_power.id,
            "hero_id": hero_power.hero_id,
            "power_id": hero_power.power_id,
            "strength": hero_power.strength,
            "power": {
                "id": hero_power.power.id,
                "name": hero_power.power.name,
                "description": hero_power.power.description
            }
        })
    
    return jsonify({
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": hero_powers_data
    })

# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_data = []
    for power in powers:
        powers_data.append({
            "id": power.id,
            "name": power.name,
            "description": power.description
        })
    return jsonify(powers_data)

# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    
    return jsonify({
        "id": power.id,
        "name": power.name,
        "description": power.description
    })

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    
    data = request.get_json()
    if 'description' not in data:
        return jsonify({"errors": ["description is required"]}), 400
    
    # Update the description
    power.description = data['description']
    db.session.commit()
        
    return jsonify({
        "id": power.id,
        "name": power.name,
        "description": power.description
    })

# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['strength', 'power_id', 'hero_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"errors": [f"{field} is required"]}), 400
    
    # Check if hero and power exist
    hero = Hero.query.get(data['hero_id'])
    power = Power.query.get(data['power_id'])
    
    # Validate strength value
    valid_strengths = ['Strong', 'Weak', 'Average']
    if data['strength'] not in valid_strengths:
        return jsonify({"errors": [f"strength must be one of: {', '.join(valid_strengths)}"]}), 422
    
    hero_power = HeroPower(
        strength=data['strength'],
        hero_id=data['hero_id'],
        power_id=data['power_id']
    )
        
    db.session.add(hero_power)
    db.session.commit()
        
    # Return the response as specified
    return jsonify({
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
    }), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)