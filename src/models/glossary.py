import json
from pathlib import Path
from typing import List, Optional
from utils import get_logger

logger = get_logger(__name__)


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
    def __init__(self, json_path: Optional[str] = None):
        self.terms = {}

        # デフォルトのJSONパス
        if json_path is None:
            # src/models/glossary.pyから見たパス
            current_dir = Path(__file__).parent
            json_path = current_dir.parent / "resources" / "glossary.json"

        self.load_terms_from_json(str(json_path))

    def load_terms_from_json(self, json_path: str):
        """JSONファイルから用語を読み込み"""
        try:
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
                logger.info(f"用語集を読み込みました: {len(self.terms)}件")
        except FileNotFoundError:
            logger.error(f"用語集ファイルが見つかりません: {json_path}")
        except json.JSONDecodeError as e:
            logger.error(f"用語集ファイルの形式が不正です: {e}")
        except Exception as e:
            logger.error(f"用語集の読み込みに失敗しました: {e}")

    def add_term(self, term: GlossaryTerm):
        """用語を追加"""
        self.terms[term.term] = term

    def get_term(self, term_name: str) -> Optional[GlossaryTerm]:
        """特定の用語を取得"""
        return self.terms.get(term_name)

    def get_all_terms(self) -> List[GlossaryTerm]:
        """すべての用語を取得"""
        return list(self.terms.values())

    def search(self, query: str) -> List[GlossaryTerm]:
        """
        用語を検索

        Args:
            query: 検索クエリ（部分一致、大文字小文字無視）

        Returns:
            マッチした用語のリスト
        """
        if not query:
            return self.get_all_terms()

        query_lower = query.lower()
        results = []

        for term in self.terms.values():
            # 用語名、短い説明、詳細説明から検索
            if (
                query_lower in term.term.lower()
                or query_lower in term.short_desc.lower()
                or query_lower in term.description.lower()
            ):
                results.append(term)

        return results
