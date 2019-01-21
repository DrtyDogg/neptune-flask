from app import app, db
from app.models import User, Feeding, WaterChange, Temperature, Aquarium


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Feeding': Feeding, 'WaterChange': WaterChange, 'Temperature': Temperature, 'Aquarium': Aquarium}
