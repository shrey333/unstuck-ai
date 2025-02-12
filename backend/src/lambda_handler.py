import json
from mangum import Mangum
from src.main import app

# Create Mangum handler for Lambda
handler = Mangum(app, lifespan="off")
