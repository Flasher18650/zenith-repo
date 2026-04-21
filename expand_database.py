import argparse
import json
from pathlib import Path


def collect_categories(db):
    categories = []
    for os_name, groups in db.items():
        if not isinstance(groups, dict):
            continue
        for category_name, apps in groups.items():
            if isinstance(apps, list):
                categories.append((os_name, category_name, apps))
    return categories


def expand_database(db, target_total):
    categories = collect_categories(db)
    if not categories:
        raise ValueError("Aucune categorie valide trouvee dans le JSON.")

    per_category = target_total // len(categories)
    remainder = target_total % len(categories)

    total_built = 0
    for idx, (os_name, category_name, apps) in enumerate(categories):
        desired = per_category + (1 if idx < remainder else 0)
        if desired <= 0:
            db[os_name][category_name] = []
            continue

        source = apps if apps else [{
            "name": f"App {os_name} {category_name}",
            "desc": "Entree generee automatiquement",
            "amd64": "https://example.com/download",
        }]

        generated = []
        source_len = len(source)
        for i in range(desired):
            base = dict(source[i % source_len])
            base_name = base.get("name", "App")
            base_desc = base.get("desc", "Sans description")
            base["name"] = f"{base_name} #{i + 1}"
            base["desc"] = f"{base_desc} (genere {i + 1})"
            generated.append(base)

        db[os_name][category_name] = generated
        total_built += len(generated)

    return total_built


def main():
    parser = argparse.ArgumentParser(
        description="Agrandit database.json a un total d'entrees choisi."
    )
    parser.add_argument(
        "--input",
        default="database.json",
        help="Fichier JSON source (defaut: database.json)",
    )
    parser.add_argument(
        "--output",
        default="database_expanded.json",
        help="Fichier JSON de sortie (defaut: database_expanded.json)",
    )
    parser.add_argument(
        "--total",
        type=int,
        required=True,
        help="Nombre total d'apps voulu dans toute la base",
    )
    args = parser.parse_args()

    if args.total < 1:
        raise ValueError("--total doit etre >= 1")

    input_path = Path(args.input)
    output_path = Path(args.output)

    with input_path.open("r", encoding="utf-8") as f:
        db = json.load(f)

    total = expand_database(db, args.total)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"OK: {total} apps ecrites dans {output_path}")


if __name__ == "__main__":
    main()
