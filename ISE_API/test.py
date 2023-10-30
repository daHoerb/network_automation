import requests
import json
import yaml
import decouple
from decouple import config
import os


# Verwenden Sie den absoluten Pfad zur .env-Datei

api_base_url = config("api_base_url")
print(f"Der Wert aus der .env Datei: {api_base_url}")

