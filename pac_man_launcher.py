from pathlib import Path
import os
import sys

from pac_man.__main__ import main


if getattr(sys, "frozen", False):
    runtime_dir = Path(sys._MEIPASS)
else:
    runtime_dir = Path(__file__).resolve().parent

os.chdir(runtime_dir)

if len(sys.argv) == 1:
    sys.argv.append(str(runtime_dir / "data" / "config.json"))

raise SystemExit(main())