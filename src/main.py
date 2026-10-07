# =============================================================================
# main.py
# Entrypoint: python main.py <command>
# No business logic — registers CLI commands and runs the Click app.
# =============================================================================

from engine.cli.commands import cli

if __name__ == "__main__":
    cli()