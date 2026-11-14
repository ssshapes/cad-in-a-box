# CAD in a box: instructions for Claude

You are setting up, and then working in, a small kit for driving FreeCAD (parametric CAD) and Blender (rendering and animation) from Claude Code. The person who cloned this may not be a developer. Explain what you are doing in plain words, one step at a time, and ask before installing anything.

## When the user says "set me up"

Work through these in order. After each step, say what you did and whether it worked.

1. **Find out what machine this is.** Mac, Windows, Linux, or Windows with WSL (Linux inside Windows). On WSL, install and run both apps on the Windows side: that is where the graphics card is, and both apps can be called from WSL as `.exe` files.

2. **Install FreeCAD 1.1 or newer** if it is not already there. Ask first.
   - Mac: `brew install --cask freecad`
   - Windows: `winget install FreeCAD.FreeCAD`
   - Linux: the AppImage or Flatpak from https://www.freecad.org/downloads.php
   Then find the command-line runner, `freecadcmd` (Windows: `freecadcmd.exe` in FreeCAD's `bin` folder; Mac: `FreeCAD.app/Contents/Resources/bin/freecadcmd`). Record its full path below under "Paths on this machine."

3. **Install Blender 5.1 or newer** if it is not already there. Ask first.
   - Mac: `brew install --cask blender`
   - Windows: `winget install BlenderFoundation.Blender`
   - Linux: the download from https://www.blender.org/download/ or Snap/Flatpak
   Find the `blender` executable and record its full path below.

4. **Prove FreeCAD works.** Run the example part, with no window:
   ```
   freecadcmd -c "exec(open('examples/freecad_plate.py').read())"
   ```
   It must print `OK plate:` and leave `plate.FCStd`, `plate.step` and `plate.stl` in `out/`. A volume of about 8568.5 mm3 means the geometry is right.

5. **Prove Blender works.** Render that part:
   ```
   blender --background --factory-startup --python examples/blender_turntable.py -- out/plate.stl
   ```
   It must print `OK still:` and leave `out/plate.png`. Open the image and look at it. A blank or all-white picture is a failure even if the command succeeded. The log says whether it rendered on the GPU or the CPU; both are fine, the GPU is just faster.

6. **Tell the user it worked** and show them the picture. Then offer the optional live connections below. Most people will not need them.

7. **Fill in "Paths on this machine"** at the bottom of this file so future sessions do not have to search again.

## How to work here

**Default to scripts, not the live connections.** For anything real, write a Python script and run the app with no window (`freecadcmd -c "exec(open('script.py').read())"` or `blender --background --python script.py`). Scripts are faster, they can be rerun after a change, and they keep working when a live connection drops. Save every script you write into `work/` so the user has a record.

**Show the user what you made.** After building or changing a part, render it with `examples/blender_turntable.py` and show the image. Do not ask them to open FreeCAD to check.

**The FreeCAD workflow is parametric.** Use the PartDesign workbench: Body, sketch, Pad or Pocket, then Fillet or Chamfer. Name things. Read back the volume and face count after each step and check them against what the user asked for.

## Traps that each cost a real retry

- **FreeCAD renumbers edges and faces** whenever an earlier feature changes. Never hard-code `Edge7`. Find edges by their geometry, as the fillet step in `examples/freecad_plate.py` does.
- **`freecadcmd path/to/script.py` can silently run nothing** on some builds. Use `-c "exec(open('path').read())"`, which always runs.
- **FreeCAD's STEP import renames duplicate parts** by bumping a trailing number, so a second copy of `PART-1961` can come in as `PART-1992`. That invents part numbers that don't exist. Before importing an assembly, set the preference: `App.ParamGet("User parameter:BaseApp/Preferences/Document").SetBool("DuplicateLabels", True)`.
- **CAD files are in millimetres; Blender works in metres.** Scale imports by 0.001, or the lights and camera will be a thousand times off.
- **Blender with no window can't use its Workbench or EEVEE renderers** on some machines; they crash for lack of a display. Use Cycles, which works anywhere.
- **Blender with no window ignores the GPU you picked in its settings.** The script has to switch the GPU on itself (the example does).
- **Use absolute output paths with forward slashes** on Windows. Relative paths can resolve to the root of C:.
- **A big assembly can take minutes to convert to a mesh.** Set a long timeout, or export only the parts you need.

## Optional: live connections

These let Claude look at what is open on the screen. They're good for asking "what's in this file?" They're not reliable enough to build with: they drop, and they leave stray processes behind.

- **FreeCAD:** https://github.com/neka-nat/freecad-mcp. Copy its `addon/FreeCADMCP` folder into FreeCAD's `Mod` folder, restart FreeCAD, switch to the "MCP Addon" workbench and click Start RPC Server. Then `claude mcp add freecad -- uvx freecad-mcp` (needs `uv`). Check the project's README; its own instructions are written for Claude Desktop.
- **Blender:** the official server from Blender Lab, https://www.blender.org/lab/mcp-server/. Follow that page.
- **Safety:** Blender's own page warns that its connection runs whatever code the model writes, with no guardrails, and recommends a machine with nothing sensitive on it. Take that seriously. The same is true of the FreeCAD one.

## Paths on this machine

(Fill in during setup.)
- freecadcmd:
- blender:
