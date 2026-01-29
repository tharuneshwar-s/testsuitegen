import logging
from typing import List

from fastapi import APIRouter

from backend.src.models.intents import IntentMetadata, MetadataResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/metadata/intents", response_model=MetadataResponse)
async def get_intents():
    """Get available test intents for UI selector."""
    intents: List[IntentMetadata] = []

    try:
        # Try to import official enums from testsuitegen
        from testsuitegen.src.generators.intent_generator.openapi_intent.enums import (
            OpenAPISpecIntentType,
        )
        from testsuitegen.src.generators.intent_generator.python_intent.enums import (
            PythonIntentType,
        )

        def humanize(name: str) -> str:
            return name.replace("_", " ").capitalize()

        def categorize(name: str) -> str:
            n = name.upper()
            if "INJECTION" in n or "SQL" in n or "XSS" in n:
                return "Security"
            if "NULL" in n:
                return "Nullability"
            if any(
                k in n for k in ("REQUIRED", "MISSING", "TYPE", "UNEXPECTED", "FORMAT")
            ):
                return "Structure"
            if any(
                k in n for k in ("BOUNDARY", "MIN", "MAX", "NUMBER", "ENUM", "PATTERN")
            ):
                return "Constraints"
            return "Functional"

        # Prefer a categorized dict if provided by testsuitegen. This allows
        # the core library to declare categories rather than relying on heuristics.
        seen = set()
        try:
            from testsuitegen.src.generators.intent_generator.openapi_intent.enums import (
                INTENTS_BY_CATEGORY as OPENAPI_INTENTS_BY_CATEGORY,
            )
        except Exception:
            OPENAPI_INTENTS_BY_CATEGORY = None

        try:
            from testsuitegen.src.generators.intent_generator.python_intent.enums import (
                INTENTS_BY_CATEGORY as PYTHON_INTENTS_BY_CATEGORY,
            )
        except Exception:
            PYTHON_INTENTS_BY_CATEGORY = None

        # Merge any available categorized mappings
        merged_mapping = {}
        for mapping in (OPENAPI_INTENTS_BY_CATEGORY, PYTHON_INTENTS_BY_CATEGORY):
            if not mapping:
                continue
            for cat, items in mapping.items():
                merged_mapping.setdefault(cat, [])
                for name in items:
                    if name not in merged_mapping[cat]:
                        merged_mapping[cat].append(name)

        if merged_mapping:
            # Use the explicit categories provided by testsuitegen
            for cat, items in merged_mapping.items():
                for name in items:
                    if name in seen:
                        continue
                    seen.add(name)
                    intents.append(
                        IntentMetadata(
                            id=name,
                            category=cat,
                            description=humanize(name),
                            default_selected=True if name == "HAPPY_PATH" else False,
                        )
                    )
        else:
            # Fallback: collect unique names from both enums and use heuristics
            for enum_cls in (OpenAPISpecIntentType, PythonIntentType):
                for member in enum_cls:
                    name = member.value if hasattr(member, "value") else member.name
                    if name in seen:
                        continue
                    seen.add(name)
                    intents.append(
                        IntentMetadata(
                            id=name,
                            category=categorize(name),
                            description=humanize(name),
                            default_selected=True if name == "HAPPY_PATH" else False,
                        )
                    )

    except Exception as e:
        # Import failed; fall back to a small, safe default set
        logger.warning("Could not load intents dynamically: %s", e)
        intents = [
            IntentMetadata(
                id="HAPPY_PATH",
                category="Functional",
                description="Happy Path (default)",
                default_selected=True,
            ),
            IntentMetadata(
                id="TYPE_VIOLATION",
                category="Structure",
                description="Type errors and mismatches",
            ),
            IntentMetadata(
                id="SQL_INJECTION",
                category="Security",
                description="SQL injection attempts",
            ),
        ]

    # derive categories from intents dynamically
    categories = sorted({i.category for i in intents if i.category})
    return MetadataResponse(
        intents=intents, categories=categories, total_count=len(intents)
    )
