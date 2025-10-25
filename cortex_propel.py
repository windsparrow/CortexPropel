"""CortexPropel - AI-powered task management system."""

import os
import sys
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cortex_propel.cli.main import main as cli_main
from cortex_propel.cli.interactive import main as interactive_main


def main():
    """Main entry point for CortexPropel."""
    parser = argparse.ArgumentParser(description="CortexPropel - AI-powered task management system")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Start in interactive mode")
    
    # Parse known args to allow the CLI to handle its own args
    args, remaining = parser.parse_known_args()
    
    if args.interactive or not remaining:
        # Start interactive mode if requested or no arguments provided
        interactive_main()
    else:
        # Pass remaining args to the CLI
        sys.argv = [sys.argv[0]] + remaining
        cli_main()


if __name__ == "__main__":
    main()