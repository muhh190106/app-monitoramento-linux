import argparse
import json

from .summary import summarize


def main():
    parser = argparse.ArgumentParser(description="Demonstração sem coleta real")
    parser.add_argument("--demo", action="store_true", help="Resumir dados fictícios")
    args = parser.parse_args()
    if not args.demo:
        parser.print_help()
        return
    events = [
        {"app": "Editor", "seconds": 120, "afk": False},
        {"app": "Navegador", "seconds": 60, "afk": False},
        {"app": "Editor", "seconds": 30, "afk": True},
    ]
    print(json.dumps({"demo": True, "active_seconds": summarize(events)}, indent=2))


if __name__ == "__main__":
    main()
