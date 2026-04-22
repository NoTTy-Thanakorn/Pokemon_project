# Project Overview: Pokemon Mystic Route

## Summary
- Developer: Thanakorn (6810545620)
- Course: Computer Programming II (01219116)
- YouTube Demo: [Link to your video]
- Proposal PDF: [Link to your PDF in GitHub]

## Motivation
The motivation behind this project was to combine randomized level design with classic RPG mechanics. I wanted to implement the Recursive Backtracker algorithm for maze generation and integrate it with an Object-Oriented battle system that handles complex data logging for player behavior analysis.

## OOP Implementation
1. Encapsulation: Pokemon statistics, move sets, and states are strictly managed within Pokemon and Move classes.
2. Modular Design: Separate modules for World generation, Battle logic, and DataManager for clean and maintainable code.
3. State Management: The game uses a state-machine pattern (Title -> Starter -> World -> Battle -> Stats).

## Data Component
The game collects and visualizes 6 key metrics to evaluate game balance:
1. Encounter Frequency: Analyzed via histograms.
2. Move Type Usage: Visualized with pie charts.
3. Exploration Trends: Steps per run tracked via line graphs.
4. Battle Balance: HP remaining and Battle duration analyzed via bar charts and boxplots.

## External Sources
- Framework: Pygame
- Analysis Tools: Matplotlib, Numpy
- Assets: Custom 8-bit procedural sprites.
