import json
from pathlib import Path

ENTITIES_PATH = Path("config/entities.json")

def load_entities() -> dict:
    return json.loads(ENTITIES_PATH.read_text())["creators"]

def resolve_entity(entity_id: str) -> dict | None:
    return load_entities().get(entity_id)

def get_all_entities() -> dict:
    return load_entities()
