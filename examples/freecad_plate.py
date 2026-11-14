# A small test part, built with FreeCAD's parametric PartDesign workflow and no window.
# 60 x 40 x 5 mm plate, a 12 x 8 grid of 3 mm through-holes, R3 fillets on the four corners.
# Writes plate.FCStd, plate.step and plate.stl to the output folder.
#
# Run (the output folder is optional; default is ./out next to this repo):
#   freecadcmd -c "exec(open('examples/freecad_plate.py').read())"
#   CAD_OUT=/some/folder freecadcmd -c "exec(open('examples/freecad_plate.py').read())"
#
# Why exec(open(...)) instead of passing the script path: on some FreeCAD builds a bare
# script path silently runs nothing. This form always runs.
import os
import FreeCAD as App
import Part, Sketcher, Mesh, Import

out = os.path.abspath(os.environ.get("CAD_OUT", "out"))
os.makedirs(out, exist_ok=True)

doc = App.newDocument("plate")
body = doc.addObject("PartDesign::Body", "Body")
xy = doc.getObject("XY_Plane")

# 1. Base plate: a closed rectangle sketch, padded 5 mm.
sk = body.newObject("Sketcher::SketchObject", "Base")
sk.AttachmentSupport = (xy, [""]); sk.MapMode = "FlatFace"
P = [App.Vector(0, 0, 0), App.Vector(60, 0, 0), App.Vector(60, 40, 0), App.Vector(0, 40, 0)]
for i in range(4):
    sk.addGeometry(Part.LineSegment(P[i], P[(i + 1) % 4]))
for i in range(4):
    sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
pad = body.newObject("PartDesign::Pad", "Pad"); pad.Profile = sk; pad.Length = 5
doc.recompute()

# 2. Holes: 96 circles in one sketch, pocketed through all.
hs = body.newObject("Sketcher::SketchObject", "Holes")
hs.AttachmentSupport = (xy, [""]); hs.MapMode = "FlatFace"
x0, y0 = 30 - 11 * 4.5 / 2, 20 - 7 * 4.5 / 2
hs.addGeometry([Part.Circle(App.Vector(x0 + c * 4.5, y0 + r * 4.5, 0), App.Vector(0, 0, 1), 1.5)
                for r in range(8) for c in range(12)])
pk = body.newObject("PartDesign::Pocket", "Pocket"); pk.Profile = hs; pk.Type = "ThroughAll"; pk.Reversed = True
doc.recompute()
if pk.Shape.Volume > 11999:  # the pocket cut nothing because it went the wrong way; flip it
    pk.Reversed = False; doc.recompute()

# 3. Fillet the four vertical corner edges. Edges are found by geometry, not by name,
#    because FreeCAD renumbers edges whenever an earlier feature changes.
shp = pk.Shape
corners = [f"Edge{i + 1}" for i, e in enumerate(shp.Edges)
           if e.Curve.__class__.__name__ == "Line" and abs(e.Length - 5) < 1e-6
           and min(abs(e.Vertexes[0].X - a) for a in (0, 60)) < 1e-6
           and min(abs(e.Vertexes[0].Y - b) for b in (0, 40)) < 1e-6]
fl = body.newObject("PartDesign::Fillet", "Fillet"); fl.Base = (pk, corners); fl.Radius = 3
doc.recompute()

s = fl.Shape
assert s.isValid(), "final solid is not valid"
assert len(corners) == 4, f"expected 4 corner edges, found {len(corners)}"

doc.saveAs(os.path.join(out, "plate.FCStd"))
Import.export([fl], os.path.join(out, "plate.step"))
Mesh.export([fl], os.path.join(out, "plate.stl"))
print(f"OK plate: volume {s.Volume:.1f} mm3, {len(s.Faces)} faces, written to {out}")
App.closeDocument(doc.Name)
