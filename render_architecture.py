"""
Render a professional architecture diagram for the AI-Assisted Underwriting Agent.
No emoji — clean text labels with colour-coded sections.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Canvas ────────────────────────────────────────────────────────────────────
FW, FH = 28, 16
fig, ax = plt.subplots(figsize=(FW, FH))
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis("off")
fig.patch.set_facecolor("#f0f4f8")
ax.set_facecolor("#f0f4f8")

# ── Colour palette ────────────────────────────────────────────────────────────
C = dict(
    navy       = "#1e3a5f",
    navy2      = "#2d5282",
    blue_sec   = "#dbeafe",
    blue_brd   = "#2563eb",
    blue_hdr   = "#1d4ed8",
    green_dk   = "#166534",
    green_bg   = "#f0fdf4",
    green_brd  = "#16a34a",
    red_dk     = "#991b1b",
    red_brd    = "#ef4444",
    slate      = "#374151",
    slate_bg   = "#f1f5f9",
    slate_brd  = "#64748b",
    purple_bg  = "#faf5ff",
    purple_brd = "#7c3aed",
    purple_hdr = "#6d28d9",
    orange_bg  = "#fff7ed",
    orange_brd = "#ea580c",
    orange_hdr = "#c2410c",
    pink_bg    = "#fce7f3",
    pink_brd   = "#9d174d",
    white      = "#ffffff",
    arrow      = "#475569",
    text_dk    = "#0f172a",
    text_wh    = "#ffffff",
    mid        = "#334155",
)

# ── Drawing helpers ───────────────────────────────────────────────────────────
def rbox(x, y, w, h, fc, ec, lw=1.8, radius=0.22, zorder=3, alpha=1.0):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={radius}",
                       facecolor=fc, edgecolor=ec, linewidth=lw,
                       alpha=alpha, zorder=zorder)
    ax.add_patch(p)
    return p

def label(x, y, w, h, top, bot=None, tc="#0f172a",
          fs=11, bold=False, zorder=4):
    fw = "bold" if bold else "normal"
    if bot:
        ax.text(x+w/2, y+h*0.60, top, ha="center", va="center",
                fontsize=fs, fontweight=fw, color=tc, zorder=zorder,
                linespacing=1.35)
        ax.text(x+w/2, y+h*0.22, bot, ha="center", va="center",
                fontsize=fs-1.5, color=tc, zorder=zorder,
                linespacing=1.25, alpha=0.88)
    else:
        ax.text(x+w/2, y+h/2, top, ha="center", va="center",
                fontsize=fs, fontweight=fw, color=tc, zorder=zorder,
                linespacing=1.35)

def node(x, y, w, h, top, bot=None,
         fc=C["white"], ec=C["slate_brd"], lw=1.8,
         tc=C["text_dk"], fs=11, bold=False, radius=0.22, zorder=3):
    rbox(x, y, w, h, fc, ec, lw, radius, zorder)
    label(x, y, w, h, top, bot, tc, fs, bold, zorder+1)

def section_header(x, y, w, h, title, bg, brd, hdr_fc, hdr_tc=C["text_wh"],
                   hdr_h=0.48, fs=11, zorder=1):
    """Section rectangle with a coloured header bar."""
    rbox(x, y, w, h, bg, brd, lw=2.2, radius=0.3, zorder=zorder)
    rbox(x, y+h-hdr_h, w, hdr_h, hdr_fc, brd, lw=0, radius=0.3, zorder=zorder+1)
    ax.text(x+w/2, y+h-hdr_h/2, title, ha="center", va="center",
            fontsize=fs, fontweight="bold", color=hdr_tc, zorder=zorder+2)

def arr(x1, y1, x2, y2, lbl="", col=C["arrow"], lw=1.7,
        rad=0.0, fs=7.5, lbl_col=None):
    if lbl_col is None:
        lbl_col = col
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                mutation_scale=12,
                                connectionstyle=f"arc3,rad={rad}"),
                zorder=6)
    if lbl:
        mx = (x1+x2)/2 + rad*(y2-y1)*0.35
        my = (y1+y2)/2 + rad*(x2-x1)*0.15 + 0.10
        ax.text(mx, my, lbl, ha="center", va="bottom",
                fontsize=fs, color=lbl_col,
                bbox=dict(boxstyle="round,pad=0.12",
                          fc="#ffffff", ec="none", alpha=0.9),
                zorder=7)

def dash_arr(x1, y1, x2, y2, lbl="", col=C["blue_brd"], lw=1.5, fs=7.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                linestyle="dashed", mutation_scale=11,
                                connectionstyle="arc3,rad=0.0"),
                zorder=6)
    if lbl:
        mx, my = (x1+x2)/2, (y1+y2)/2+0.12
        ax.text(mx, my, lbl, ha="center", va="bottom",
                fontsize=fs, color=col,
                bbox=dict(boxstyle="round,pad=0.12",
                          fc="#ffffff", ec="none", alpha=0.9),
                zorder=7)

# ═════════════════════════════════════════════════════════════════════════════
# TITLE BAR
# ═════════════════════════════════════════════════════════════════════════════
node(0.3, 14.85, 27.4, 0.9,
     "AI-Assisted Underwriting  —  Multi-Agent Architecture on Databricks",
     fc=C["navy"], ec=C["navy"], tc=C["text_wh"],
     fs=16, bold=True, radius=0.3, zorder=5)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — USER INTERFACE   x: 0.3–5.3
# ═════════════════════════════════════════════════════════════════════════════
section_header(0.3, 1.2, 5.0, 13.2,
               "USER INTERFACE  —  Underwriting Workspace",
               C["blue_sec"], C["blue_brd"], C["blue_hdr"])

node(0.7, 12.4, 4.2, 1.35,
     "Applicant & Application", "Browser",
     fc=C["white"], ec=C["blue_brd"], tc=C["navy"], fs=11, bold=True)

node(0.7, 10.55, 4.2, 1.35,
     "AI Analysis  (One-Click)", None,
     fc=C["white"], ec=C["blue_brd"], tc=C["navy"], fs=11.5, bold=True)

# Human Decision header
node(0.7, 9.85, 4.2, 0.55,
     "Human Decision Panel",
     fc=C["navy"], ec=C["navy"], tc=C["text_wh"], fs=10.5, bold=True, radius=0.15)

node(0.7, 9.05, 1.2, 0.7, "Approve",
     fc=C["green_dk"], ec=C["green_dk"], tc=C["text_wh"], fs=11, bold=True)
node(2.05, 9.05, 1.2, 0.7, "Deny",
     fc=C["red_dk"], ec=C["red_dk"], tc=C["text_wh"], fs=11, bold=True)
node(3.4, 9.05, 1.5, 0.7, "Approve w/\nChanges",
     fc=C["slate"], ec=C["slate"], tc=C["text_wh"], fs=10, bold=True)

node(0.7, 7.8, 4.2, 0.95,
     "Decision Audit Trail",
     fc=C["white"], ec=C["blue_brd"], tc=C["navy"], fs=11)

# UI arrows
arr(2.8, 12.4,  2.8, 11.9,  col=C["blue_brd"])
arr(2.8, 10.55, 2.8, 10.4,  col=C["blue_brd"])
# AI Analysis → decisions
arr(1.3,  10.55, 1.3, 9.75,  col=C["blue_brd"])
arr(2.65, 10.55, 2.65, 9.75, col=C["blue_brd"])
arr(4.15, 10.55, 4.15, 9.75, col=C["blue_brd"])
# decisions → audit
arr(1.3,  9.05, 1.3,  8.75,  col=C["arrow"])
arr(2.65, 9.05, 2.65, 8.75,  col=C["arrow"])
arr(4.15, 9.05, 4.15, 8.75,  col=C["arrow"])
arr(2.8, 8.75,  2.8,  8.75,  col=C["arrow"])
# collect to single point then to audit
ax.plot([1.3, 4.15], [8.75, 8.75], color=C["arrow"], lw=1.5, zorder=5)
arr(2.8, 8.75, 2.8, 8.75, col=C["arrow"])
arr(2.8, 8.75, 2.8, 7.8+0.95, col=C["blue_brd"])

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ORCHESTRATOR   x: 5.8–10.8
# ═════════════════════════════════════════════════════════════════════════════
section_header(5.8, 7.2, 5.0, 7.2,
               "ORCHESTRATOR",
               "#eef2ff", C["navy"], C["navy"])

node(6.2, 11.4, 4.2, 1.8,
     "Orchestrator Agent", "OpenAI Agents SDK",
     fc=C["navy"], ec=C["navy2"], tc=C["text_wh"], fs=12, bold=True, radius=0.3)

node(6.2, 9.9, 4.2, 1.1,
     "Tool Router",
     fc=C["navy2"], ec=C["navy"], tc=C["text_wh"], fs=11.5, bold=True)

node(6.2, 8.55, 1.95, 0.9,
     "MLflow Tracing",
     fc=C["slate_bg"], ec=C["slate_brd"], tc=C["mid"], fs=10)

node(8.35, 8.55, 2.05, 0.9,
     "FMAPI Model\nClaude / Llama / GPT",
     fc=C["slate_bg"], ec=C["slate_brd"], tc=C["mid"], fs=10)

# Orch arrows
arr(8.3, 11.4, 8.3, 11.0,  col=C["navy"])
arr(8.3, 9.9,  8.3, 9.45,  col=C["navy"])

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — SUB-AGENTS   x: 11.2–19.7
# ═════════════════════════════════════════════════════════════════════════════
section_header(11.2, 1.2, 8.5, 13.2,
               "SUB-AGENTS",
               "#f8f9ff", C["navy2"], C["navy2"])

# ── Genie MCP ─────────────────────────────────────────────────────────────────
section_header(11.5, 9.5, 7.9, 4.6,
               "Genie MCP  —  Structured Data via Natural Language SQL",
               C["blue_sec"], C["blue_hdr"], C["blue_hdr"], fs=10.5)

node(11.8, 10.8, 3.2, 2.8,
     "Natural Language\nSQL Engine\n(Genie MCP)",
     fc=C["blue_hdr"], ec=C["blue_hdr"], tc=C["text_wh"], fs=11.5, bold=True, radius=0.3)

node(15.5, 13.1, 3.6, 0.65, "dim_applicant  |  fact_application",
     fc=C["white"], ec=C["blue_brd"], tc=C["blue_hdr"], fs=10)
node(15.5, 12.15, 3.6, 0.65, "fact_underwriting_decision  |  dim_product",
     fc=C["white"], ec=C["blue_brd"], tc=C["blue_hdr"], fs=10)
node(15.5, 11.2, 3.6, 0.65, "ref_underwriting_limits  |  ref_reason_code",
     fc=C["white"], ec=C["blue_brd"], tc=C["blue_hdr"], fs=10)

arr(15.0, 12.2, 15.5, 13.425, col=C["blue_brd"], lw=1.2)
arr(15.0, 12.2, 15.5, 12.475, col=C["blue_brd"], lw=1.2)
arr(15.0, 12.2, 15.5, 11.525, col=C["blue_brd"], lw=1.2)

# ── UC Functions ──────────────────────────────────────────────────────────────
section_header(11.5, 5.2, 7.9, 4.0,
               "UC Functions  —  Governed Business Rules",
               C["purple_bg"], C["purple_brd"], C["purple_hdr"], fs=10.5)

node(11.8, 6.5, 2.8, 2.3,
     "UC Functions\nGoverned\nBusiness Rules",
     fc=C["purple_hdr"], ec=C["purple_hdr"], tc=C["text_wh"], fs=11.5, bold=True, radius=0.3)

node(15.2, 8.35, 3.9, 0.6,
     "max_sum_assured — coverage limit",
     fc=C["white"], ec=C["purple_brd"], tc=C["purple_hdr"], fs=9.5)
node(15.2, 7.5, 3.9, 0.6,
     "risk_tier — BMI + smoker risk",
     fc=C["white"], ec=C["purple_brd"], tc=C["purple_hdr"], fs=9.5)
node(15.2, 6.65, 3.9, 0.6,
     "ulip_smoker_blocked — eligibility",
     fc=C["white"], ec=C["purple_brd"], tc=C["purple_hdr"], fs=9.5)

arr(14.6, 7.65, 15.2, 8.65,  col=C["purple_brd"], lw=1.2)
arr(14.6, 7.65, 15.2, 7.80,  col=C["purple_brd"], lw=1.2)
arr(14.6, 7.65, 15.2, 6.95,  col=C["purple_brd"], lw=1.2)

# ── Vector Search RAG ─────────────────────────────────────────────────────────
section_header(11.5, 1.5, 7.9, 3.4,
               "Vector Search RAG  —  Policy Documents",
               C["orange_bg"], C["orange_brd"], C["orange_hdr"], fs=10.5)

node(11.8, 2.15, 2.8, 2.3,
     "Vector Search\nRAG\nPolicy Docs",
     fc=C["orange_hdr"], ec=C["orange_hdr"], tc=C["text_wh"], fs=11.5, bold=True, radius=0.3)

node(15.2, 3.9, 3.9, 0.6,
     "Underwriting Manuals",
     fc=C["white"], ec=C["orange_brd"], tc=C["orange_hdr"], fs=10)
node(15.2, 3.05, 3.9, 0.6,
     "Product Guidelines",
     fc=C["white"], ec=C["orange_brd"], tc=C["orange_hdr"], fs=10)
node(15.2, 2.2, 3.9, 0.6,
     "Compliance Checklists",
     fc=C["white"], ec=C["orange_brd"], tc=C["orange_hdr"], fs=10)

arr(14.6, 3.3, 15.2, 4.2,  col=C["orange_brd"], lw=1.2)
arr(14.6, 3.3, 15.2, 3.35, col=C["orange_brd"], lw=1.2)
arr(14.6, 3.3, 15.2, 2.5,  col=C["orange_brd"], lw=1.2)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DATA LAYER   x: 20.1–27.4
# ═════════════════════════════════════════════════════════════════════════════
section_header(20.1, 1.2, 7.2, 13.2,
               "DATA LAYER  —  Unity Catalog",
               C["green_bg"], C["green_brd"], C["green_dk"])

node(20.5, 12.35, 6.4, 1.6,
     "Unity Catalog", "Governance  |  Lineage  |  Access Control",
     fc=C["green_dk"], ec=C["green_dk"], tc=C["text_wh"], fs=12, bold=True, radius=0.3)

node(20.5, 10.1, 6.4, 1.8,
     "Delta Tables", "Structured applicant & underwriting data",
     fc=C["white"], ec=C["green_brd"], tc=C["green_dk"], fs=11.5, bold=True)

node(20.5, 7.9, 6.4, 1.8,
     "UC Functions", "Governed business rule UDFs",
     fc=C["white"], ec=C["purple_brd"], tc=C["purple_hdr"], fs=11.5, bold=True)

node(20.5, 5.7, 6.4, 1.8,
     "Volumes", "Underwriting manuals & policy documents",
     fc=C["white"], ec=C["orange_brd"], tc=C["orange_hdr"], fs=11.5, bold=True)

node(20.5, 3.5, 6.4, 1.8,
     "Vector Search Index", "Embedding store for RAG retrieval",
     fc=C["white"], ec=C["green_brd"], tc=C["green_dk"], fs=11.5, bold=True)

# UC internal arrows
arr(23.7, 12.35, 23.7, 11.9,  col=C["green_dk"])
arr(23.7, 10.1,  23.7, 9.7,   col=C["green_dk"])
arr(23.7, 7.9,   23.7, 7.5,   col=C["purple_hdr"])
arr(23.7, 5.7,   23.7, 5.3,   col=C["orange_hdr"])

# ═════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT STRIP (bottom)
# ═════════════════════════════════════════════════════════════════════════════
rbox(0.3, 0.1, 27.4, 0.95, C["pink_bg"], C["pink_brd"], lw=2, radius=0.25, zorder=2)
ax.text(14.0, 0.80, "DEPLOYMENT & SECURITY",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color=C["pink_brd"], zorder=4)

deploy_items = [
    "Databricks App  |  DAB Deploy",
    "Service Principal Authentication",
    "Per-User Isolation",
    "MLflow Experiment Tracking",
]
dxs = [0.5, 7.3, 14.1, 20.9]
for txt, dx in zip(deploy_items, dxs):
    node(dx, 0.15, 6.5, 0.55, txt,
         fc=C["white"], ec=C["pink_brd"], tc=C["pink_brd"], fs=10, radius=0.18)

# ═════════════════════════════════════════════════════════════════════════════
# CROSS-SECTION ARROWS
# ═════════════════════════════════════════════════════════════════════════════

# UI (AI Analysis centre) --> Orchestrator Agent  (two parallel horizontal arrows)
arr(4.9, 11.4, 6.2, 11.7, lbl="REST API request",
    col=C["blue_hdr"], lw=2.2, fs=10.5)

# Orchestrator response back (dashed, slightly lower)
dash_arr(6.2, 11.2, 4.9, 10.95, lbl="AI response",
         col=C["blue_brd"], lw=1.6, fs=10)

# Tool Router --> Genie  (straight up-right)
arr(10.8, 10.45, 11.8, 12.2, lbl="NL query",
    col=C["blue_hdr"], lw=2, rad=0.0, fs=10.5)

# Tool Router --> UC Functions  (straight across)
arr(10.8, 10.0, 11.8, 7.65, lbl="rules check",
    col=C["purple_hdr"], lw=2, rad=0.0, fs=10.5)

# Tool Router --> RAG  (straight down-right)
arr(10.8, 9.9, 11.8, 3.3, lbl="doc search",
    col=C["orange_hdr"], lw=2, rad=0.0, fs=10.5)

# Genie tables --> Delta Tables
arr(19.1, 12.475, 20.5, 11.0, lbl="reads",
    col=C["blue_brd"], lw=1.8, fs=10)
arr(19.1, 11.525, 20.5, 11.0, col=C["blue_brd"], lw=1.3)

# UC Functions --> UC Data layer
arr(19.1, 8.35, 20.5, 8.8, lbl="calls",
    col=C["purple_brd"], lw=1.8, fs=10)
arr(19.1, 7.5,  20.5, 8.8, col=C["purple_brd"], lw=1.3)

# RAG docs --> Volumes
arr(19.1, 3.9, 20.5, 6.6, lbl="retrieves",
    col=C["orange_brd"], lw=1.8, fs=10)
# Compliance Checklists --> Vector Search Index
arr(19.1, 2.5, 20.5, 4.4, lbl="indexed",
    col=C["green_brd"], lw=1.8, fs=10)

# ═════════════════════════════════════════════════════════════════════════════
# COLUMN HEADER LABELS (above section boxes)
# ═════════════════════════════════════════════════════════════════════════════
for xc, lbl in [
    (2.8,  "1  USER\nINTERFACE"),
    (8.3,  "2  ORCHESTRATOR"),
    (15.45,"3  SUB-AGENTS"),
    (23.7, "4  DATA LAYER"),
]:
    ax.text(xc, 14.6, lbl, ha="center", va="center",
            fontsize=10, fontweight="bold", color=C["slate_brd"],
            linespacing=1.2, zorder=8)

# ═════════════════════════════════════════════════════════════════════════════
# SAVE
# ═════════════════════════════════════════════════════════════════════════════
out_png = "/Users/sarbani.maiti/underwriting-agent/architecture.png"
out_hires = "/Users/sarbani.maiti/underwriting-agent/architecture_hires.png"
plt.tight_layout(pad=0)
plt.savefig(out_png, dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor(), edgecolor="none")
plt.savefig(out_hires, dpi=300, bbox_inches="tight",
            facecolor=fig.get_facecolor(), edgecolor="none")
print(f"Saved: {out_png}")
print(f"Saved hi-res: {out_hires}")
