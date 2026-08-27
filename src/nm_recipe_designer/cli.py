from __future__ import annotations

import argparse
import json
from pathlib import Path

from .builder import design_recipe
from .convert import normalize_recipe
from .validate import validate_recipe


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(prog="nm-recipe-designer")
    sub = parser.add_subparsers(dest="command", required=True)

    design = sub.add_parser("design", help="Create a baseline recipe")
    design.add_argument("description")
    design.add_argument("--rows", type=int, default=100)
    design.add_argument("--mode", choices=["auto", "text", "code", "structured"], default="auto")
    design.add_argument("--language", default="auto")
    design.add_argument("--model", default="")
    design.add_argument("--endpoint", default="")
    design.add_argument("-o", "--output")

    validate = sub.add_parser("validate", help="Validate a recipe locally")
    validate.add_argument("path")

    normalize = sub.add_parser("normalize", help="Normalize Data Designer JSON for Unsloth import")
    normalize.add_argument("path")

    args = parser.parse_args()
    if args.command == "design":
        result = design_recipe(args.description, rows=args.rows, response_mode=args.mode, code_language=args.language, model=args.model, endpoint=args.endpoint)
    elif args.command == "validate":
        result = validate_recipe(_load(args.path))
    else:
        result = normalize_recipe(_load(args.path))

    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if getattr(args, "output", None):
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
