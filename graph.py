"""
graph.py  –  generates all required graphs from data.json.
Run standalone:  python graph.py
Graphs saved to screenshots/visualization/
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUT = "screenshots/visualization"
os.makedirs(OUT, exist_ok=True)

TYPE_COLORS = {
    "fire":"#E85020","water":"#3280F0","grass":"#30B840",
    "electric":"#F8C800","psychic":"#D050B8","rock":"#A08C50",
    "ghost":"#6840A8","normal":"#A09888",
}


def load():
    if not os.path.exists("data.json"):
        print("data.json not found"); return None
    with open("data.json","r",encoding="utf-8") as f:
        return json.load(f)


def style():
    plt.rcParams.update({
        "figure.facecolor":"#1a1a2e","axes.facecolor":"#16213e",
        "axes.edgecolor":"#4a4a6a","axes.labelcolor":"white",
        "xtick.color":"white","ytick.color":"white",
        "text.color":"white","grid.color":"#2a2a4a",
        "grid.linestyle":"--","grid.alpha":0.5,
        "font.family":"DejaVu Sans",
    })


# ── Graph 1: Steps per run (Line) ─────────────────────────────────────────
def graph_steps(data):
    steps = data.get("steps_per_run",[])
    if not steps: steps=[0]
    fig,ax=plt.subplots(figsize=(10,5))
    ax.plot(range(1,len(steps)+1),steps,color="#60c8ff",linewidth=2,marker="o",markersize=5)
    ax.fill_between(range(1,len(steps)+1),steps,alpha=0.2,color="#60c8ff")
    ax.set_title("Steps Walked per Run",fontsize=16,pad=12)
    ax.set_xlabel("Run Number"); ax.set_ylabel("Steps")
    ax.grid(True); fig.tight_layout()
    fig.savefig(f"{OUT}/steps_per_run.png",dpi=120); plt.close(fig)
    print("Saved: steps_per_run.png")


# ── Graph 2: Encounters per run (Histogram) ───────────────────────────────
def graph_encounters(data):
    enc=data.get("encounters_per_run",[])
    if not enc: enc=[0]
    fig,ax=plt.subplots(figsize=(10,5))
    ax.hist(enc,bins=max(5,len(set(enc))),color="#50d890",edgecolor="#1a1a2e",rwidth=0.85)
    ax.set_title("Distribution of Wild Encounters per Run",fontsize=16,pad=12)
    ax.set_xlabel("Number of Encounters"); ax.set_ylabel("Frequency")
    ax.grid(True,axis="y"); fig.tight_layout()
    fig.savefig(f"{OUT}/encounters_histogram.png",dpi=120); plt.close(fig)
    print("Saved: encounters_histogram.png")


# ── Graph 3: Move type usage (Pie) ───────────────────────────────────────
def graph_move_types(data):
    mt=data.get("move_type_usage",{})
    if not mt: mt={"normal":1}
    labels=list(mt.keys()); vals=list(mt.values())
    colors=[TYPE_COLORS.get(l,"#888888") for l in labels]
    fig,ax=plt.subplots(figsize=(8,7))
    wedges,texts,autotexts=ax.pie(
        vals,labels=labels,colors=colors,autopct="%1.1f%%",
        startangle=140,pctdistance=0.82,
        wedgeprops={"edgecolor":"#1a1a2e","linewidth":1.5}
    )
    for t in texts+autotexts: t.set_color("white"); t.set_fontsize(12)
    ax.set_title("Elemental Move Usage (All Runs)",fontsize=16,pad=16)
    fig.tight_layout(); fig.savefig(f"{OUT}/move_type_pie.png",dpi=120); plt.close(fig)
    print("Saved: move_type_pie.png")


# ── Graph 4: HP remaining at battle end (Bar) ────────────────────────────
def graph_hp(data):
    hp=data.get("hp_remaining",[])
    if not hp: hp=[0]
    fig,ax=plt.subplots(figsize=(10,5))
    x=range(1,len(hp)+1)
    colors=["#50d890" if h>15 else "#f8c800" if h>5 else "#e85050" for h in hp]
    ax.bar(x,hp,color=colors,edgecolor="#1a1a2e",width=0.7)
    ax.axhline(np.mean(hp),color="#60c8ff",linestyle="--",linewidth=2,label=f"Mean: {np.mean(hp):.1f}")
    ax.set_title("HP Remaining at End of Each Battle",fontsize=16,pad=12)
    ax.set_xlabel("Battle Number"); ax.set_ylabel("HP Remaining")
    ax.legend(); ax.grid(True,axis="y"); fig.tight_layout()
    fig.savefig(f"{OUT}/hp_remaining.png",dpi=120); plt.close(fig)
    print("Saved: hp_remaining.png")


# ── Graph 5: Battle duration (Boxplot) ───────────────────────────────────
def graph_duration(data):
    dur=data.get("battle_durations",[])
    if not dur: dur=[0]
    fig,ax=plt.subplots(figsize=(8,6))
    bp=ax.boxplot(dur,patch_artist=True,
                  boxprops={"facecolor":"#6040c0","color":"white"},
                  whiskerprops={"color":"white"},capprops={"color":"white"},
                  medianprops={"color":"#f8c800","linewidth":2},
                  flierprops={"markerfacecolor":"#e85050","marker":"o"})
    ax.set_title("Battle Duration Distribution (seconds)",fontsize=16,pad=12)
    ax.set_ylabel("Duration (seconds)"); ax.set_xticklabels(["All Battles"])
    ax.grid(True,axis="y"); fig.tight_layout()
    fig.savefig(f"{OUT}/battle_duration_boxplot.png",dpi=120); plt.close(fig)
    print("Saved: battle_duration_boxplot.png")


# ── Summary table (Win/Loss/Catches) ─────────────────────────────────────
def graph_summary(data):
    labels=["Total Runs","Wins","Losses","Total Catches","Best Party"]
    vals=[data.get("runs",0),data.get("wins",0),data.get("losses",0),
          data.get("total_catches",0),data.get("best_team_size",0)]
    colors=["#9090d0","#50d890","#e85050","#f8c800","#60c8ff"]
    fig,ax=plt.subplots(figsize=(10,5))
    bars=ax.bar(labels,vals,color=colors,edgecolor="#1a1a2e",width=0.55)
    for bar,v in zip(bars,vals):
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.05,
                str(v),ha="center",va="bottom",fontsize=13,color="white",fontweight="bold")
    ax.set_title("Overall Run Statistics",fontsize=16,pad=12)
    ax.set_ylabel("Count"); ax.grid(True,axis="y"); fig.tight_layout()
    fig.savefig(f"{OUT}/run_summary.png",dpi=120); plt.close(fig)
    print("Saved: run_summary.png")


def main():
    style()
    d=load()
    if not d: return
    graph_steps(d); graph_encounters(d); graph_move_types(d)
    graph_hp(d); graph_duration(d); graph_summary(d)
    print(f"\nAll graphs saved to  {OUT}/")

if __name__=="__main__":
    main()