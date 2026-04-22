# Pokemon Mystic Route

## Project Description
- Project by: Thanakorn Innok (6810545620)
- Game Genre: 2D Turn-based RPG / Adventure

Pokemon Mystic Route is a 2D adventure game developed using Python and Pygame. It features a procedurally generated maze where players explore, encounter wild Pokemon, and build a team to challenge a legendary boss. The project integrates randomized world logic with a full Object-Oriented battle system and data tracking for performance analysis.

---

## Installation
To Clone this project:
git clone https://github.com/NoTTy-Thanakorn/Pokemon_project.git

To create and run Python Environment for This project:

[Window]
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

[Mac/Linux]
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

---

## Running Guide
After activate Python Environment of this project, you can process to run the game by:

[Window]
python main.py

[Mac/Linux]
python3 main.py

---

## Tutorial / Usage
1. Title Screen: Press ENTER to start a new game or H to view your play history.
2. Starter Selection: Choose your partner by pressing 1 (Fire), 2 (Water), or 3 (Grass).
3. Exploration: Use Arrow Keys to move. Walk into dark green grass tiles to encounter wild Pokemon.
4. Capturing: Win a battle to add that Pokemon to your party (Maximum 6).
5. Boss Battle: Once your team is full (6 members), find the gate at the right edge of the maze and press B to fight the Boss.
6. Battle Controls: 
   - UP/DOWN to select a move.
   - SPACE to attack.
   - T to switch Pokemon.

---

## Game Features
- Procedural Maze Generation: A new, unique map every time you play using Recursive Backtracker algorithm.
- Turn-based Combat: Strategic elemental system (Fire > Grass > Water).
- Data Persistence: Automatically saves every gameplay session to data.json.

---

## Known Bugs
- In rare cases, the randomized maze might generate a narrow corridor near grass tiles, but the Boss Gate is always reachable from the starting point.

---

## External Sources
- Framework: Pygame
- Data Analysis: Matplotlib, Numpy
# Pokemon_project
