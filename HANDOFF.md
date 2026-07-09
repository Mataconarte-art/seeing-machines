# Seeing Machines · L1–L3 — Publishing Handoff

**Author:** Mateo Acevedo · CompSci for Designers 2 · TH Nürnberg · Summer 2026
**Purpose:** package this consolidated repo, add the corpus, publish to GitHub + Pages, and export a PDF.

---

## 0. What this folder is

`seeing-machines/` is the **complete, self-contained write-up of all three levels** (The Finder,
The Companion, The Critic). One `index.html`, one `README.md`, seven figures regenerated from the
committed artifacts, the L1/L2/L3 notebooks, and the L2 + L3 artifact sets. The only thing missing is
the corpus images (yours to add), because the archive is not redistributed publicly.

---

## 1. Add the corpus, then zip

1. Put a **20-image sample** in `corpus/sample/` (brief requirement), and/or the full set in
   `corpus/images/`. Update `corpus/README.md` if you link a shared folder instead.
2. Compress the whole `seeing-machines/` directory to `seeing-machines.zip`.

> Note on size: the three notebooks carry their embedded outputs (~65 MB total). That's fine for
> GitHub (well under the 100 MB/file limit) but makes the zip large — if you only need the *documentation*
> published, you can exclude `notebooks/` from the zip and keep them locally.

---

## 2. Publish to GitHub

```bash
cd seeing-machines
git init -b main
git add .
git commit -m "Seeing Machines L1-L3: consolidated write-up, artifacts, figures, notebooks"
# create an empty repo on github.com (suggested name: seeing-machines), then:
git remote add origin https://github.com/<your-username>/seeing-machines.git
git push -u origin main
```

The `.pkl` files are ~0.7 MB and ~0.35 MB; notebooks are ~20–27 MB each — all under GitHub's
100 MB/file limit, so no Git LFS needed. (If you'd rather not commit the images, add
`corpus/images/` to a `.gitignore` before the first commit.)

### Enable GitHub Pages
Repo → **Settings → Pages** → Source: **Deploy from a branch** → Branch: **main** / **/(root)** → Save.
After ~1 minute the site is live at `https://<your-username>.github.io/seeing-machines/`
(`index.html` serves automatically; `.nojekyll` keeps `figures/` intact).

### Export the PDF (submit alongside the link)
Open the live Pages URL in Chrome → **Print → Save as PDF** → Background graphics **on**, margins Default.
Save as `SeeingMachines_L1-L3_Acevedo.pdf`.

---

## 3. Repo name note

This folder currently lives inside a parent named `seeing-machines-l2` (its previous scope). The
consolidated repo covers all three levels, so the suggested GitHub repo name is **`seeing-machines`**.
The folder name doesn't affect the site; rename the repo on GitHub as you like.

---

## 4. Reproduce the figures (optional sanity check)

```bash
pip install matplotlib
python figures/make_figures.py   # regenerates all 7 PNGs from artifacts/
```

Every figure in `index.html` and `README.md` is produced by this one script from the committed
`artifacts/` — nothing is hand-drawn except `figures/pipeline.svg`.
