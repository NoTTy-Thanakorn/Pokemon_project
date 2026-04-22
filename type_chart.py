"""type_chart.py"""
_chart={
    ("fire","grass"):2.0,("fire","rock"):0.5,("fire","water"):0.5,("fire","fire"):0.5,
    ("water","fire"):2.0,("water","rock"):2.0,("water","water"):0.5,("water","grass"):0.5,("water","electric"):0.5,
    ("grass","water"):2.0,("grass","rock"):2.0,("grass","fire"):0.5,("grass","grass"):0.5,
    ("electric","water"):2.0,("electric","grass"):0.5,("electric","electric"):0.5,("electric","rock"):0.5,
    ("psychic","normal"):2.0,("psychic","ghost"):0.0,("psychic","psychic"):0.5,
    ("rock","fire"):2.0,("rock","grass"):0.5,("rock","water"):0.5,
    ("ghost","psychic"):2.0,("ghost","normal"):0.0,("ghost","ghost"):2.0,
    ("normal","ghost"):0.0,("normal","rock"):0.5,
}
def get_multiplier(a,b): return _chart.get((a,b),1.0)