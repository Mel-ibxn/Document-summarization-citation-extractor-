import re
from typing import Dict, List, Set

class CitationExtractor:
    """
    Extracts legal citations (cases, sections, acts, years, courts) from text
    using regular expressions.
    """

    def __init__(self):
        # Regex Patterns
        self.patterns = {
            "cases": [
                # Case names like "Ramesh vs. State", "X v. Y", "A versus B"
                # Allows for lowercase words like 'of', 'and', 'the' in the names
                r"([A-Z][a-z]*(?:\s+(?:[A-Z][a-z]*|of|and|the))*\s+(?:v\.|vs\.|versus)\s+[A-Z][a-z]*(?:\s+(?:[A-Z][a-z]*|of|and|the))*)",
            ],
            "sections": [
                # Section patterns: Section 302, Sec. 302, u/s 302, Section 302(1)(a)
                r"(?:Section|Sec\.|u/s)\s+(\d+[A-Z]?(?:\(\d+\)[a-z]?)?)",
            ],
            "acts": [
                # Common Acts: Indian Penal Code, IPC, CrPC, CPC, Constitution of India
                r"(?:Indian Penal Code|IPC|Code of Criminal Procedure|CrPC|Code of Civil Procedure|CPC|Constitution of India|Narcotic Drugs and Psychotropic Substances Act|NDPS)",
            ],
            "years": [
                # Years in brackets or accompanying SCC/AIR: (2020), 2021 SCC, 1999 AIR
                r"(\(\d{4}\))",
                r"(\d{4}\s+(?:SCC|AIR|SCALE|JT))",
            ],
            "courts": [
                # Court names
                r"((?:Supreme Court|High Court|District Court)(?:\s+of\s+[A-Z][a-z]+)?)",
            ]
        }

    def extract_all(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts all citation types from the text, deduplicates them,
        and returns a dictionary grouped by type.
        """
        results = {
            "cases": set(),
            "sections": set(),
            "acts": set(),
            "years": set(),
            "courts": set()
        }

        # Categories that should be case-insensitive
        case_insensitive_cats = {"acts", "courts", "sections"}

        for category, patterns in self.patterns.items():
            flags = re.IGNORECASE if category in case_insensitive_cats else 0
            for pattern in patterns:
                matches = re.finditer(pattern, text, flags)
                for match in matches:
                    found = match.group(0).strip()
                    if found:
                        results[category].add(found)

        # Convert sets back to sorted lists for consistent output
        return {k: sorted(list(v)) for k, v in results.items()}

    def format_results(self, extracted: Dict[str, List[str]]) -> str:
        """Helper to format extracted citations into a readable string."""
        lines = []
        for category, items in extracted.items():
            if items:
                lines.append(f"{category.capitalize()}:")
                for item in items:
                    lines.append(f"  - {item}")
        return "\n".join(lines)

if __name__ == "__main__":
    # Basic smoke test
    extractor = CitationExtractor()
    sample = """
    In the case of Ramesh vs. State of Maharashtra, the Supreme Court 
    referred to Section 302 of the Indian Penal Code (IPC). 
    The judgment was recorded in (2020) and cited 2021 SCC. 
    Another reference was made to Sec. 420 of the CrPC.
    """
    
    found = extractor.extract_all(sample)
    print(extractor.format_results(found))
