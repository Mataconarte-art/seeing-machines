#!/usr/bin/env python3
"""Regenerate every figure in this repo from the committed artifacts.

    pip install matplotlib
    python figures/make_figures.py

Produces (in figures/):
  L2 : age_distribution.png, occasion_distribution.png, route_comparison.png, caption_saga.png
  L3 : alpha_sweep.png, precision_at_k.png, per_query_precision.png
Palette matches the write-up: visual=#c08457, caption=#4a6b7c, hybrid/accent=#b5533b.
"""
import json, os, collections
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ART  = os.path.join(HERE, "..", "artifacts")
OUT  = HERE

BG="#faf7f2"; INK="#1c1a17"; MUTE="#6b6459"; LINE="#e7e1d6"
VIS="#c08457"; CAP="#4a6b7c"; HYB="#b5533b"
plt.rcParams.update({
    "figure.facecolor":BG,"axes.facecolor":BG,"savefig.facecolor":BG,
    "axes.edgecolor":LINE,"axes.labelcolor":INK,"text.color":INK,
    "xtick.color":MUTE,"ytick.color":MUTE,"font.size":11,
    "axes.grid":True,"grid.color":LINE,"grid.linewidth":.8,
    "axes.spines.top":False,"axes.spines.right":False,
})
def load(*p): 
    with open(os.path.join(ART,*p)) as f: return json.load(f)
def save(fig,name): fig.tight_layout(); fig.savefig(os.path.join(OUT,name),dpi=150); plt.close(fig)

# ============================= L2 =============================
caps = load("captions.json")
recs = list(caps.values()) if isinstance(caps,dict) else caps

# 1. age distribution
ab = collections.Counter(str(r.get("subject_age_band")).strip().lower() for r in recs)
order = ["child","teenager","young adult","adult"]
items = [(k,ab.get(k,0)) for k in order if ab.get(k,0)] + \
        [(k,v) for k,v in ab.most_common() if k not in order]
labels=[k for k,_ in items]; vals=[v for _,v in items]
fig,ax=plt.subplots(figsize=(8,4.2))
bars=ax.bar(labels,vals,color=VIS,zorder=3)
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+1.5,str(v),ha="center",fontsize=11,color=INK)
ax.set_ylabel("images"); ax.set_title("L2 · subject_age_band across the 227 images",color=INK,fontweight="bold",loc="left")
ax.grid(axis="x",visible=False); ax.set_ylim(0,max(vals)*1.15)
save(fig,"age_distribution.png")

# 2. occasion distribution
oc = collections.Counter(str(r.get("occasion")).strip().lower() for r in recs)
oi = oc.most_common()
labels=[k for k,_ in oi]; vals=[v for _,v in oi]
fig,ax=plt.subplots(figsize=(8,4.4))
cols=[MUTE]+[CAP]*(len(labels)-1)   # highlight "none" in muted
bars=ax.bar(labels,vals,color=cols,zorder=3)
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+1.5,str(v),ha="center",fontsize=10,color=INK)
ax.set_ylabel("images"); ax.set_title("L2 · occasion field — sparse by design (none = 133/227)",color=INK,fontweight="bold",loc="left")
ax.grid(axis="x",visible=False); ax.set_ylim(0,max(vals)*1.15)
plt.setp(ax.get_xticklabels(),rotation=25,ha="right",fontsize=9)
save(fig,"occasion_distribution.png")

# 3. route comparison (top-1 per query, CLIP vs caption)
rc = load("l2_route_comparison.json")
queries=list(rc.keys())
clip1=[rc[q]["clip"][0]["score"] for q in queries]
cap1 =[rc[q]["caption"][0]["score"] for q in queries]
y=np.arange(len(queries))[::-1]; h=0.36
fig,ax=plt.subplots(figsize=(8.6,4.8))
ax.barh(y+h/2,cap1,h,color=CAP,label="caption (text)",zorder=3)
ax.barh(y-h/2,clip1,h,color=VIS,label="CLIP (visual)",zorder=3)
for yy,v in zip(y+h/2,cap1): ax.text(v+0.008,yy,f"{v:.2f}",va="center",fontsize=9,color=INK)
for yy,v in zip(y-h/2,clip1): ax.text(v+0.008,yy,f"{v:.2f}",va="center",fontsize=9,color=INK)
ax.set_yticks(y); ax.set_yticklabels(queries,fontsize=10)
ax.set_xlabel("top-1 cosine similarity"); ax.set_xlim(0,0.8)
ax.set_title("L2 · top-1 similarity per query — different scales, different picks",color=INK,fontweight="bold",loc="left",fontsize=12)
ax.legend(frameon=False,loc="center right",fontsize=10); ax.grid(axis="y",visible=False)
save(fig,"route_comparison.png")

# 4. caption saga (parse yield)
runs=["clean run\n(2026-07-06)","scale-up\n(2026-07-08)"]
total=[227,1462]; ok=[227,628]
x=np.arange(2); w=0.5
fig,ax=plt.subplots(figsize=(7.4,4.3))
ax.bar(x,total,w,color=LINE,zorder=2,label="attempted")
b=ax.bar(x,ok,w,color=[CAP,HYB],zorder=3,label="valid JSON")
for xi,t,o in zip(x,total,ok):
    ax.text(xi,t+18,f"{o}/{t}\n({o/t*100:.0f}%)",ha="center",fontsize=11,color=INK,fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(runs); ax.set_ylabel("images")
ax.set_title("L2 · structured-JSON caption yield — reliable at 227, brittle at 1462",color=INK,fontweight="bold",loc="left",fontsize=11.5)
ax.set_ylim(0,1650); ax.grid(axis="x",visible=False); ax.legend(frameon=False,loc="upper left",fontsize=9)
save(fig,"caption_saga.png")

# ============================= L3 =============================
routes=["visual_only","caption_only","hybrid"]
labs={"visual_only":"visual only","caption_only":"caption only","hybrid":"hybrid (α=0.3)"}
cols={"visual_only":VIS,"caption_only":CAP,"hybrid":HYB}

# 5. alpha sweep
sw=load("l3","alpha_sweep.json"); xs=[p["alpha"] for p in sw["sweep"]]; ys=[p["precision@5"] for p in sw["sweep"]]
best=sw["best_alpha"]; bi=xs.index(best)
fig,ax=plt.subplots(figsize=(8,4.2))
ax.plot(xs,ys,"-o",color=HYB,lw=2.2,ms=6,zorder=3)
ax.scatter([best],[ys[bi]],s=180,color=HYB,zorder=4,edgecolor="white",linewidth=1.5)
ax.annotate(f"best α = {best}\nP@5 = {ys[bi]:.3f}",(best,ys[bi]),xytext=(best+0.06,ys[bi]+0.02),fontsize=11,color=INK,fontweight="bold")
ax.axvline(best,color=MUTE,ls=":",lw=1)
ax.annotate("α=0\n(caption only)",(0,ys[0]),xytext=(0.01,ys[0]-0.06),fontsize=9,color=CAP)
ax.annotate("α=1\n(visual only)",(1,ys[-1]),xytext=(0.80,ys[-1]+0.02),fontsize=9,color=VIS)
ax.set_xlabel("α  (weight on visual route:  hybrid = α·visual + (1−α)·caption)"); ax.set_ylabel("precision@5 (gold set)")
ax.set_title("L3 · α-sweep — fusion beats either route alone",color=INK,fontweight="bold",loc="left")
ax.set_xticks([i/10 for i in range(11)]); ax.set_ylim(0.15,0.65)
save(fig,"alpha_sweep.png")

# 6. precision@k
ev=load("l3","evaluation_results.json"); ks=["p@1","p@3","p@5"]
x=np.arange(len(ks)); w=0.26
fig,ax=plt.subplots(figsize=(8,4.4))
for i,r in enumerate(routes):
    vals=[ev["precision_at_k"][r][k] for k in ks]
    bars=ax.bar(x+(i-1)*w,vals,w,label=labs[r],color=cols[r],zorder=3)
    for bb,v in zip(bars,vals): ax.text(bb.get_x()+bb.get_width()/2,v+0.01,f"{v:.3f}",ha="center",va="bottom",fontsize=9,color=INK)
ax.set_xticks(x); ax.set_xticklabels([k.upper() for k in ks]); ax.set_ylabel("precision"); ax.set_ylim(0,1.0)
ax.set_title("L3 · precision@k across the three routes (8-query gold set)",color=INK,fontweight="bold",loc="left")
ax.legend(frameon=False,ncol=3,loc="upper right",fontsize=10); ax.grid(axis="x",visible=False)
save(fig,"precision_at_k.png")

# 7. per-query precision@5
pq=ev["per_query"]; queries=list(pq.keys()); y=np.arange(len(queries))[::-1]; h=0.26
fig,ax=plt.subplots(figsize=(8.5,5.2))
for i,r in enumerate(routes):
    vals=[pq[q][r] for q in queries]
    ax.barh(y+(i-1)*h,vals,h,label=labs[r],color=cols[r],zorder=3)
ax.set_yticks(y); ax.set_yticklabels(queries,fontsize=10); ax.set_xlabel("precision@5"); ax.set_xlim(0,1.05)
ax.set_title("L3 · per-query precision@5  (8-query gold set)",color=INK,fontweight="bold",loc="left",fontsize=12)
ax.legend(frameon=False,ncol=3,loc="lower right",fontsize=9); ax.grid(axis="y",visible=False)
save(fig,"per_query_precision.png")

print("wrote:", sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
