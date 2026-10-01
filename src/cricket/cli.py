from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .critic import CRITIC_PROMPT
from .models import ReviewRequest
from .render import render_blockquote
from .reviewer import Cricket


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cricket")
    sub = parser.add_subparsers(dest="command", required=True)
    review = sub.add_parser("review", help="review a JSON request")
    review.add_argument("request", help="path to request JSON or '-' for stdin")
    review.add_argument("--json", action="store_true", help="emit structured JSON")
    review.add_argument("--speak-on-pass", action="store_true")
    sub.add_parser("prompt", help="print the semantic critic prompt contract")
    return parser


def _load_request(path: str) -> ReviewRequest:
    if path == "-":
        raw = json.load(sys.stdin)
    else:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return ReviewRequest.from_dict(raw)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prompt":
        print(CRITIC_PROMPT)
        return 0
    request = _load_request(args.request)
    result = Cricket().review(request)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        rendered = render_blockquote(result, speak_on_pass=args.speak_on_pass)
        if rendered:
            print(rendered)
    return 2 if result.disposition.value == "BLOCK" else 1 if result.disposition.value == "CHALLENGE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
