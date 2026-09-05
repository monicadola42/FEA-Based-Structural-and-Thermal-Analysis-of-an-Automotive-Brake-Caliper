"""
Parametric Automotive Disc Brake Caliper
==========================================
EA-Based Structural and Thermal Analysis of an Automotive Brake Caliper using ANSYS

CAD engine : CadQuery 2.x (Python, built on the OpenCASCADE kernel)
Output     : brake_caliper.step  (import this into ANSYS Workbench > Geometry)
             brake_caliper.stl   (quick visual preview only, NOT for ANSYS)

--------------------------------------------------------------------------
HOW TO RUN THIS SCRIPT
--------------------------------------------------------------------------
1. Install CadQuery (pick ONE):

   A) pip (simplest):
        pip install cadquery

   B) conda (use this if pip fails — most reliable on Windows):
        conda create -n caliper -c conda-forge -c cadquery cadquery=2.4 python=3.11
        conda activate caliper

   Optional but recommended for a beginner: also install CQ-editor, a free
   graphical viewer for CadQuery, so you can SEE the model and re-run the
   script interactively while you learn:
        pip install cq-editor

2. Run:
        python brake_caliper_parametric.py

   Two files appear next to the script: brake_caliper.step and
   brake_caliper.stl. Open the STEP file in ANSYS Workbench > Geometry.

3. To change the design later (for your "design improvement" study),
   edit any value in the PARAMETERS block below and re-run. Everything
   downstream (bores, cavities, fillets, ribs) recomputes automatically.

--------------------------------------------------------------------------
IF A FILLET FAILS
--------------------------------------------------------------------------
Fillet operations are the most common failure point in any parametric
CAD kernel (OCC included) once several features intersect near the same
edge. This script wraps every fillet in `safe_fillet()`, which retries
at a smaller radius and, as a last resort, skips it and prints a warning
instead of crashing. If you see a "[warn]" message when you run the
script, open the STEP file in ANSYS SpaceClaim/DesignModeler (or in
CQ-editor) and manually round that specific edge — it will not affect
the rest of the geometry.
"""

import cadquery as cq

# ===========================================================================
# 1. PARAMETERS  (all dimensions in millimeters — edit these for redesigns)
# ===========================================================================

# --- Overall envelope -------------------------------------------------------
L        = 180.0                 # overall length of the caliper body (X)
LEG_H    = 55.0                  # height of each leg, from the bottom (Z)
BRIDGE_H = 20.0                  # height of the bridge/yoke above the legs
H        = LEG_H + BRIDGE_H      # overall height (Z)  -> 75 mm

# --- Legs (piston housings) and disc/pad clearance --------------------------
WALL_T   = 25.0                  # thickness of EACH leg (Y direction)
DISC_GAP = 24.0                  # clear gap between the two legs
W        = 2 * WALL_T + DISC_GAP # overall width (Y)   -> 74 mm

# --- Bridge (connects the tops of the two legs) -----------------------------
BRIDGE_MARGIN = 20.0              # bridge inset from each end of the body (X)

# --- Piston bores (2 per leg, opposed-piston fixed caliper) -----------------
BORE_D        = 42.0              # piston bore diameter
BORE_DEPTH    = 18.0              # blind bore depth (leaves a back wall)
BORE_OFFSET_X = 45.0              # bore centre distance from the nearest end

# --- Pad cavity (pocket that houses the brake-pad backing plate) ------------
PAD_CAVITY_L = 120.0              # pad cavity length, X
PAD_CAVITY_H = 40.0               # pad cavity height, Z
PAD_CAVITY_D = 6.0                # pad cavity pocket depth, Y

# --- Mounting bosses / bolt holes (vertical bolts into the caliper base) ----
MOUNT_HOLE_D    = 14.0            # mounting hole diameter (M12 clearance)
MOUNT_BOSS_D    = 26.0            # mounting boss outer diameter
MOUNT_BOSS_PROJ = 10.0            # boss projection below the body (Z)
MOUNT_SPACING   = 130.0           # centre-to-centre spacing of the 2 holes (X)
MOUNT_HOLE_PENETRATION = 15.0     # how far the blind hole goes up into the leg

# --- Ribs (stiffening fins on the outer/top face of the bridge) -------------
RIB_T  = 6.0                      # rib thickness, X
RIB_H  = 10.0                     # rib height above the bridge surface, Z
N_RIBS = 4                        # number of ribs, evenly spaced on the bridge

# --- Fillets ------------------------------------------------------------------
FILLET_OUTER = 5.0                # large fillets: outer body + pocket corners
FILLET_INNER = 3.0                # smaller fillets: leg-to-bridge transitions

# ===========================================================================
# 2. HELPER: robust fillet with automatic fallback
# ===========================================================================
def safe_fillet(wp, edge_selector, radius, label=""):
    """Apply a fillet; retry at a smaller radius if OCC rejects it; skip
    (with a warning) rather than crashing the whole script."""
    for factor in (1.0, 0.6, 0.3):
        r = radius * factor
        try:
            return wp.edges(edge_selector).fillet(r)
        except Exception as e:
            print(f"  [warn] fillet '{label}' failed at r={r:.2f} mm ({e})")
    print(f"  [warn] fillet '{label}' skipped entirely — round it manually "
          f"in ANSYS SpaceClaim/DesignModeler if needed.")
    return wp


# ===========================================================================
# 3. MAIN STRUCTURAL BODY: two legs + connecting bridge
# ===========================================================================
print("Building main body (legs + bridge)...")

# Leg A — inboard leg, Y = [0, WALL_T]
leg_a = (
    cq.Workplane("XY")
    .box(L, WALL_T, LEG_H, centered=(False, False, False))
)

# Leg B — outboard leg, Y = [WALL_T + DISC_GAP, W]
leg_b = (
    cq.Workplane("XY")
    .box(L, WALL_T, LEG_H, centered=(False, False, False))
    .translate((0, WALL_T + DISC_GAP, 0))
)

# Bridge — spans the full width (Y), sits above both legs, inset from the
# body ends in X so the legs are visible at each end (realistic proportions).
bridge = (
    cq.Workplane("XY")
    .box(L - 2 * BRIDGE_MARGIN, W, BRIDGE_H, centered=(False, False, False))
    .translate((BRIDGE_MARGIN, 0, LEG_H))
)

body = leg_a.union(leg_b).union(bridge)

# ===========================================================================
# 4. PISTON BORES — blind holes cut from the OUTER face of each leg,
#    axis parallel to Y (the clamping direction).
# ===========================================================================
print("Cutting piston bores...")

bore_centers_x = [BORE_OFFSET_X, L - BORE_OFFSET_X]
bore_z = LEG_H / 2.0

for xc in bore_centers_x:
    # Build a cylinder along +Z, then rotate -90 deg about the X axis so its
    # axis points along +Y, then translate into position.
    bore_a = (
        cq.Workplane("XY")
        .center(xc, 0)
        .circle(BORE_D / 2.0)
        .extrude(BORE_DEPTH)
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, 0, bore_z))
    )
    body = body.cut(bore_a)  # cuts inward from the Y = 0 face of leg A

    bore_b = (
        cq.Workplane("XY")
        .center(xc, 0)
        .circle(BORE_D / 2.0)
        .extrude(BORE_DEPTH)
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, W - BORE_DEPTH, bore_z))
    )
    body = body.cut(bore_b)  # cuts inward from the Y = W face of leg B

# ===========================================================================
# 5. PAD CAVITIES — shallow pockets on the INNER face of each leg
#    (the face that looks into the disc gap), for the brake-pad backing plate
# ===========================================================================
print("Cutting brake-pad cavities...")

pad_cavity_a = (
    cq.Workplane("XY")
    .box(PAD_CAVITY_L, PAD_CAVITY_D, PAD_CAVITY_H, centered=(True, False, True))
    .translate((L / 2.0, WALL_T - PAD_CAVITY_D, LEG_H / 2.0))
)
body = body.cut(pad_cavity_a)

pad_cavity_b = (
    cq.Workplane("XY")
    .box(PAD_CAVITY_L, PAD_CAVITY_D, PAD_CAVITY_H, centered=(True, False, True))
    .translate((L / 2.0, WALL_T + DISC_GAP, LEG_H / 2.0))
)
body = body.cut(pad_cavity_b)

# ===========================================================================
# 6. MOUNTING BOSSES + BOLT HOLES — vertical bosses under leg A
# ===========================================================================
print("Adding mounting bosses and bolt holes...")

mount_x = [L / 2.0 - MOUNT_SPACING / 2.0, L / 2.0 + MOUNT_SPACING / 2.0]
mount_y = WALL_T / 2.0

for xc in mount_x:
    boss = (
        cq.Workplane("XY")
        .center(xc, mount_y)
        .circle(MOUNT_BOSS_D / 2.0)
        .extrude(-MOUNT_BOSS_PROJ)
    )
    body = body.union(boss)

for xc in mount_x:
    hole = (
        cq.Workplane("XY")
        .workplane(offset=-MOUNT_BOSS_PROJ)
        .center(xc, mount_y)
        .circle(MOUNT_HOLE_D / 2.0)
        .extrude(MOUNT_BOSS_PROJ + MOUNT_HOLE_PENETRATION)
    )
    body = body.cut(hole)

# ===========================================================================
# 7. RIBS — stiffening fins on the outer (top) face of the bridge
# ===========================================================================
print("Adding stiffening ribs...")

bridge_x0 = BRIDGE_MARGIN
bridge_x1 = L - BRIDGE_MARGIN
rib_xs = [
    bridge_x0 + (bridge_x1 - bridge_x0) * (i + 1) / (N_RIBS + 1)
    for i in range(N_RIBS)
]

for xc in rib_xs:
    rib = (
        cq.Workplane("XY")
        .box(RIB_T, W, RIB_H, centered=(True, False, False))
        .translate((xc, 0, LEG_H + BRIDGE_H))
    )
    body = body.union(rib)

# ===========================================================================
# 8. FILLETS — rounded edges at stress-concentration-prone locations
# ===========================================================================
print("Applying fillets...")

# Vertical edges: rounds the outer body corners AND the pad-cavity pocket
# corners (avoids sharp internal corners, which are FE stress singularities).
body = safe_fillet(body, "|Z", FILLET_OUTER, "vertical edges")

# Edges running along the length (X): softens the leg-to-bridge junctions
# and rib bases — these are the highest-stress transition zones.
body = safe_fillet(body, "|X", FILLET_INNER, "leg-to-bridge transitions")

# ===========================================================================
# 9. EXPORT
# ===========================================================================
print("Exporting STEP and STL...")
cq.exporters.export(body, "brake_caliper.step")
cq.exporters.export(body, "brake_caliper.stl")

print("Done. Files written: brake_caliper.step, brake_caliper.stl")
print(f"Overall envelope: {L:.0f} x {W:.0f} x {H:.0f} mm (L x W x H)")
