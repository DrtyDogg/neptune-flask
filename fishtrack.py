from app import app, db
from app.models import User, Feeding, Role, WaterChange, Temperature, Aquarium

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Feeding': Feeding, 'Role': Role, 'WaterChange': WaterChange, 'Temperature': Temperature, 'Aquarium': Aquarium}
