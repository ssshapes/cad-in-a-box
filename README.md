# CAD in a box

FreeCAD and Blender, driven by [Claude Code](https://claude.com/claude-code). You describe a part, Claude builds it in FreeCAD as real parametric CAD, then renders it in Blender so you can see it. No install script: the repo tells Claude how to set itself up on your machine.

> **A note from me first.** [YOUR DISCLAIMER HERE, in your words, e.g. the line from the memory-architecture repo: not a developer, very little knowledge of good programming practice; what I bring is taste, judgment, curiosity, and a fixation with not forgetting things that are useful.] Claude wrote the code. I've been using this setup for my own product design work since October, and the notes in it are what broke along the way.

## Start

1. Install [Claude Code](https://claude.com/claude-code).
2. Clone this repo and open a terminal in it:
   ```
   git clone https://github.com/ssshapes/cad-in-a-box
   cd cad-in-a-box
   claude
   ```
3. Say **"set me up."** Claude checks your machine, asks before installing FreeCAD and Blender, builds a test part, and shows you a render of it.

Then ask for a part: "a 40 mm square mounting bracket, 3 mm thick, with two M4 holes and a 90 degree bend." You'll get the FreeCAD file, a STEP for anyone else's CAD, an STL for printing, and a picture.

## What's in it

| | |
|---|---|
| `CLAUDE.md` | The setup steps and working rules Claude follows. Read this if you want to know what it will do. |
| `examples/freecad_plate.py` | A test part: plate, 96 holes, filleted corners. Builds with no window. |
| `examples/blender_turntable.py` | Renders any STL as a studio still or a turntable. |

## Why scripts and not the live connections

Both apps have connectors that let Claude reach into a window you have open. They're fun, and good for asking "what's in this file?" Over a month of real use they also dropped often and left stray processes running. Having Claude write a script and run the app with no window has been faster and much more reliable, and every part comes with a script you can rerun. The connectors are still in `CLAUDE.md` as an option.

**One warning:** Blender's own page says its connector runs whatever code the model writes, with no guardrails. Don't run it on a machine with anything you care about.

## Tested on

Windows 11 (through WSL), FreeCAD 1.1.4, Blender 5.2.2. Mac and Linux setup steps are written but not yet tested. If you try one, tell me what broke.

## License

MIT
