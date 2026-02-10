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
from src.data_manager import load_vocab
from src.search import search_vocab

def serve():
    print("Starting Japanese Learning API Server...")
    # Using string import allows reload if needed, but here we just run it.
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Japanese Learning App")
    parser.add_argument("--headless", action="store_true", help="Run in headless JSON mode (one-shot)")
    parser.add_argument("--study", action="store_true", help="Run in headless study mode (fetch new items)")
    parser.add_argument("--get-stats", action="store_true", help="Get user stats in headless mode")
    parser.add_argument("--search", help="Search term for headless mode")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # CLI command (default if no args)
    cli_parser = subparsers.add_parser("cli", help="Run the interactive CLI")

    # Server command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search dictionary")
    search_parser.add_argument("query", help="Word to search for")

    args = parser.parse_args()

    if args.headless:
        run_headless(args)
        sys.exit(0)

    if args.command == "serve":
        serve()
    elif args.command == "cli":
        cli_main()
    elif args.command == "search":
        vocab = load_vocab()
        results = search_vocab(args.query, vocab)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # Default to CLI if no command provided, for backward compatibility
        cli_main()
