#!/usr/bin/env python3
import sys
import os
import argparse
import uvicorn

# Ensure src is in path
sys.path.append(os.path.dirname(__file__))

from src.main import main as cli_main

def serve():
    print("Starting Japanese Learning API Server...")
    # Using string import allows reload if needed, but here we just run it.
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Japanese Learning App")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # CLI command (default if no args)
    cli_parser = subparsers.add_parser("cli", help="Run the interactive CLI")

    # Server command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")

    args = parser.parse_args()

    if args.command == "serve":
        serve()
    elif args.command == "cli":
        cli_main()
    else:
        # Default to CLI if no command provided, for backward compatibility
        cli_main()
