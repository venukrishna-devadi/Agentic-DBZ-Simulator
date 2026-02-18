# What is it?
# The code inside __init__.py is importing models (classes) from other files in the same package (schemas) and making them available for import from the package itself.
# Think of it like a "shortcut" or a "re-export" mechanism.
# Why do we use it?
# Imagine you have a package schemas with several files: state.py, characters.py, battle.py, each containing some models (classes).
# Without this code, if you want to use a model, you would have to import it like this:
# Python
# from schemas.state import GameState
# from schemas.characters import Character
# from schemas.battle import BattleState
# But with this code, you can import it like this:
# Python
# from schemas import GameState, Character, BattleState
# It's like creating a shortcut to the models, so you don't have to navigate through the package structure every time.
# What is __all__?
# __all__ is a special variable in Python that defines what symbols (functions, classes, variables) are exported from a module when you use from module import *.
# In this case, __all__ is listing all the models that are being imported and re-exported from the package. It's like saying, "Hey, these are the things you can import from this package."
# So, when you use from schemas import *, it will import all the models listed in __all__.
# Why do we need both?
# We need both the imports and the __all__ list because:
# The imports bring the models into the __init__.py file.
# The __all__ list makes them available for import from the package.
# It's like a two-step process:
# Bring the models in ( imports )
# Make them available for export ( __all__ )

##  STATE MANAGEMENT WITH PYDANTIC

from schemas.state import GameState, PlanStep
from schemas.characters import Character, Player, NPC
from schemas.battle import BattleState, BattleAction, SpecialMove, Transformation

__all__ = [
    "GameState",
    "PlanStep",
    "Character",
    "Player",
    "NPC",
    "BattleState",
    "BattleAction",
    "SpecialMove",
    "Transformation"
]