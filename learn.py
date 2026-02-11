#!/usr/bin/env python3
import sys
import os
import argparse
import uvicorn
import json

# Ensure src is in path
sys.path.append(os.path.dirname(__file__))

from src.main import main as cli_main
from src.headless import run_headless

def serve():
    print("Starting Japanese Learning API Server...")
    # Using string import allows reload if needed, but here we just run it.
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)

def ingest(args):
    from src.ingest import fetch_jlpt, fetch_pitch, fetch_kanji

    if args.type == "jlpt":
        if not args.level:
            print("Please specify --level (e.g. n5, n4)")
            return
        fetch_jlpt(args.level, args.url)

    elif args.type == "pitch":
        fetch_pitch(args.url)

    elif args.type == "kanji":
        if args.char:
            fetch_kanji(args.char)
        elif args.all:
            print("Fetching all kanji is not yet implemented (needs list).")
        else:
            print("Please specify --char <kanji>")

    else:
        print("Unknown type. Use --type jlpt|pitch|kanji")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Japanese Learning App")
    parser.add_argument("--headless", action="store_true", help="Run in headless JSON mode (one-shot)")
    parser.add_argument("--study", action="store_true", help="Use Study Mode in headless (learn new items)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run the interactive CLI")

    # Server command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest data (JLPT, Pitch, Kanji)")
    ingest_parser.add_argument("--type", choices=["jlpt", "pitch", "kanji"], required=True, help="Type of data to ingest")
    ingest_parser.add_argument("--level", help="JLPT Level (e.g. n5)")
    ingest_parser.add_argument("--char", help="Kanji character to fetch")
    ingest_parser.add_argument("--all", action="store_true", help="Fetch all (for kanji)")
    ingest_parser.add_argument("--url", help="Override source URL")

    args = parser.parse_args()

    if args.headless:
        mode = "study" if args.study else "quiz"
        run_headless(mode)
        sys.exit(0)

    if args.command == "serve":
        serve()
    elif args.command == "cli":
        cli_main()
    elif args.command == "ingest":
        ingest(args)
    else:
        # Default to CLI if no command provided, for backward compatibility
        cli_main()
