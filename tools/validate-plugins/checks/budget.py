"""budget: the sum of all skill and agent descriptions stays under MAX_TOTAL_DESCRIPTION_LEN."""

from __future__ import annotations

import sys

from common import doc_files, fail, main, parse_frontmatter

# Ratchet on the sum of every skill and agent description. Lower it when the total drops; raise it
# only in the PR that adds a component, by that component's description length.
MAX_TOTAL_DESCRIPTION_LEN = 27329


def check() -> None:
    total = sum(
        len((parse_frontmatter(doc) or {}).get("description", ""))
        for doc in doc_files()
    )
    if total > MAX_TOTAL_DESCRIPTION_LEN:
        fail(
            "descriptions",
            f"total is {total} chars, over the {MAX_TOTAL_DESCRIPTION_LEN} ratchet - trim, "
            "or raise MAX_TOTAL_DESCRIPTION_LEN by the new component's description only",
        )


if __name__ == "__main__":
    sys.exit(main(check))
