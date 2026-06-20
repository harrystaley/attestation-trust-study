"""setup_env.py -- one-time environment bootstrap for the stimulus generator.

AI assistance disclosure: This utility script was generated with the assistance
of an AI assistant (Claude) and reviewed by Harry Staley. It is project setup
tooling (API-key/.env bootstrap), not graded analytical content or experimental
stimuli. Use of generative AI follows the CS 6795 course policy.

Creates a local ``.env`` file holding your OpenAI API key, and makes sure
``.env`` is git-ignored so the key never lands in your repository.

SAFETY DESIGN:
  - This script NEVER contains your key. It either writes a placeholder you
    fill in by hand, or (with --interactive) prompts you to paste it at runtime.
  - It refuses to overwrite an existing .env (so you can't clobber a real key).
  - It guarantees .env is in .gitignore before doing anything else.

Usage:
    python setup_env.py                # writes a .env template to fill in
    python setup_env.py --interactive  # prompts you to paste the key now

After running, confirm:  cat .gitignore | grep .env   ->  should list .env
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

ENV_PATH = Path(".env")
GITIGNORE_PATH = Path(".gitignore")
ENV_KEY = "OPENAI_API_KEY"
PLACEHOLDER = "paste-your-key-here"


def ensure_gitignore() -> None:
    """Make sure .env (and common secrets) are git-ignored.

    Appends entries to .gitignore if missing; creates the file if absent. This
    runs first so the key file is protected before it can ever be created.
    """
    needed = [".env", ".env.local", "*.key"]
    existing = ""
    if GITIGNORE_PATH.exists():
        existing = GITIGNORE_PATH.read_text(encoding="utf-8")

    missing = [line for line in needed if line not in existing.splitlines()]
    if not missing:
        print(".gitignore already protects .env -- good.")
        return

    with GITIGNORE_PATH.open("a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write("\n# secrets (added by setup_env.py)\n")
        for line in missing:
            f.write(line + "\n")
    print(f"Added to .gitignore: {', '.join(missing)}")


def write_env(interactive: bool) -> None:
    """Create .env if it does not already exist.

    Args:
        interactive: If True, prompt for the key at runtime (input hidden) and
            write the real value. If False, write a placeholder for you to edit.

    The script refuses to overwrite an existing .env, so a real key is never
    clobbered by re-running this.
    """
    if ENV_PATH.exists():
        print(f"{ENV_PATH} already exists -- leaving it untouched.")
        return

    if interactive:
        # getpass hides the input so the key isn't echoed to the terminal/log
        key = getpass.getpass("Paste your OpenAI API key (input hidden): ").strip()
        if not key:
            print("No key entered; writing a placeholder instead.")
            key = PLACEHOLDER
    else:
        key = PLACEHOLDER

    ENV_PATH.write_text(f"{ENV_KEY}={key}\n", encoding="utf-8")

    if key == PLACEHOLDER:
        print(f"Created {ENV_PATH} with a placeholder.")
        print(f"  -> Open it and replace '{PLACEHOLDER}' with your real key.")
    else:
        print(f"Created {ENV_PATH} with your key (hidden). It is git-ignored.")


def main() -> int:
    """Run the bootstrap: protect first, then create the env file."""
    parser = argparse.ArgumentParser(description="Bootstrap the .env for the API key.")
    parser.add_argument(
        "--interactive", action="store_true",
        help="Prompt for the key now (hidden input) instead of a placeholder.",
    )
    args = parser.parse_args()

    ensure_gitignore()       # protect BEFORE creating the secret file
    write_env(args.interactive)

    print("\nNext steps:")
    print("  1. Ensure your key is in .env (no quotes needed).")
    print("  2. In your notebook:  from dotenv import load_dotenv; load_dotenv()")
    print("  3. Then  client = OpenAI()  picks up the key automatically.")
    print("  4. NEVER commit .env -- verify with:  git status (it should not appear).")
    return 0


if __name__ == "__main__":
    sys.exit(main())