import json


class GlossaryTerm:
    def __init__(
        self, term: str, short_desc: str, description: str, related: list, command: str
    ):
        self.term = term
        self.short_desc = short_desc
        self.description = description
        self.related = related
        self.command = command


class Glossary:
    def __init__(self):
        self.terms = {}
        self.load_terms_from_json("src/models/glossary_terms.json")

    def load_terms_from_json(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data["terms"]:
                term = GlossaryTerm(
                    term=item["term"],
                    short_desc=item["short_desc"],
                    description=item["description"],
                    related=item.get("related", []),
                    command=item.get("command", ""),
                )
                self.add_term(term)

    def add_term(self, term: GlossaryTerm):
        self.terms[term.term] = term

    def get_term(self, term_name: str) -> GlossaryTerm:
        return self.terms.get(term_name)

    def get_all_terms(self) -> list:
        return list(self.terms.values())
