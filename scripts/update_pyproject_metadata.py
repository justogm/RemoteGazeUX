"""Small helper to update project metadata in pyproject.toml.

Usage:
    python scripts/update_pyproject_metadata.py --name "new-name" --version 1.2.3

If no args provided, runs interactively.
"""

import argparse
import tomllib
import tomli_w
import os

PYPROJECT = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")


def load_pyproject(path=PYPROJECT):
    with open(path, "rb") as f:
        return tomllib.load(f)


def write_pyproject(data, path=PYPROJECT):
    with open(path, "wb") as f:
        f.write(tomli_w.dumps(data).encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name")
    parser.add_argument("--version")
    parser.add_argument("--description")
    parser.add_argument("--author")
    parser.add_argument("--email")
    args = parser.parse_args()

    data = load_pyproject()
    project = data.get("project", {})

    if args.name or args.version or args.description or args.author or args.email:
        if args.name:
            project["name"] = args.name
        if args.version:
            project["version"] = args.version
        if args.description:
            project["description"] = args.description
        if args.author or args.email:
            name = args.author or project.get("authors", [{}])[0].get("name")
            email = args.email or project.get("authors", [{}])[0].get("email")
            project["authors"] = [{"name": name, "email": email}]
    else:
        # interactive
        print("Current project metadata:")
        print("Name:", project.get("name"))
        print("Version:", project.get("version"))
        print("Description:", project.get("description"))
        authors = project.get("authors", [])
        if authors:
            print("Author:", authors[0].get("name"))
            print("Email:", authors[0].get("email"))
        print("\nPress Enter to keep current value")
        name = input("New name: ").strip() or project.get("name")
        version = input("New version: ").strip() or project.get("version")
        description = input("New description: ").strip() or project.get("description")
        author = input("New author name: ").strip() or (
            authors[0].get("name") if authors else None
        )
        email = input("New author email: ").strip() or (
            authors[0].get("email") if authors else None
        )
        project["name"] = name
        project["version"] = version
        project["description"] = description
        project["authors"] = [{"name": author, "email": email}]

    data["project"] = project
    write_pyproject(data)
    print("pyproject.toml updated")


if __name__ == "__main__":
    main()
