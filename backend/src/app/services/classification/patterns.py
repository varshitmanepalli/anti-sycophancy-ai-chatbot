"""Pattern definitions for rule-based input classification.

Each category has keyword lists and regex patterns with associated weights.
Higher weight = stronger signal for that category.
"""

import re
from dataclasses import dataclass

from app.domain.classification import InputCategory


@dataclass(frozen=True)
class CategoryPattern:
    """Weighted signals for a single category."""

    keywords: tuple[str, ...] = ()
    patterns: tuple[tuple[str, float], ...] = ()  # (regex, weight)
    keyword_weight: float = 1.0


CATEGORY_PATTERNS: dict[InputCategory, CategoryPattern] = {
    InputCategory.FACT: CategoryPattern(
        keywords=(
            "what is", "what are", "who is", "who was", "when did", "when was",
            "where is", "how many", "how much", "how long", "how old",
            "define", "definition", "fact", "true that", "is it true",
            "according to", "capital of", "population of", "invented",
            "discovered", "history of", "origin of",
        ),
        patterns=(
            (r"\bwhat (?:is|are|was|were)\b", 2.5),
            (r"\bwho (?:is|was|are|were)\b", 2.5),
            (r"\bwhen (?:did|was|were|is)\b", 2.0),
            (r"\bwhere (?:is|was|are|were)\b", 2.0),
            (r"\bhow many\b", 2.0),
            (r"\bhow much\b", 1.5),
            (r"\b(is|are|was|were) .+ (true|correct|accurate)\b", 2.0),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.OPINION: CategoryPattern(
        keywords=(
            "what do you think", "do you think", "in your opinion", "i think",
            "i believe", "i feel like", "should i", "is it better", "do you agree",
            "would you say", "isn't it", "don't you think", "subjective",
            "point of view", "perspective", "prefer", "better than", "worse than",
            "good idea", "bad idea", "worth it",
        ),
        patterns=(
            (r"\bwhat do you think\b", 3.0),
            (r"\bdo you (?:think|believe|agree)\b", 2.5),
            (r"\bin my opinion\b", 2.5),
            (r"\bshould i\b", 2.0),
            (r"\bis .+ better (?:than|or)\b", 2.0),
            (r"\b(i think|i believe|i feel) (?:that )?\b", 2.0),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.PREDICTION: CategoryPattern(
        keywords=(
            "will", "going to", "predict", "prediction", "forecast", "future",
            "by 20", "next year", "in the future", "likely to", "expect to",
            "trend", "outlook", "prognosis", "anticipate", "estimate future",
            "what will happen", "going to happen",
        ),
        patterns=(
            (r"\bwhat will\b", 2.5),
            (r"\bwill .+ (?:in|by|within) \d{4}\b", 3.0),
            (r"\b(?:predict|forecast|anticipate)\b", 2.5),
            (r"\bin the (?:near )?future\b", 2.0),
            (r"\bgoing to (?:be| happen|change)\b", 2.0),
            (r"\blikely to\b", 1.5),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.PROGRAMMING: CategoryPattern(
        keywords=(
            "python", "javascript", "typescript", "java", "rust", "golang", "c++",
            "code", "function", "class", "method", "variable", "algorithm",
            "debug", "bug", "error", "exception", "compile", "runtime",
            "api", "database", "sql", "git", "docker", "kubernetes",
            "fastapi", "react", "node", "array", "loop", "recursion",
            "syntax", "framework", "library", "import", "deploy",
        ),
        patterns=(
            (r"\b(?:def|class|import|return|async|await)\b", 2.5),
            (r"\b(?:bug|debug|stack trace|traceback)\b", 2.5),
            (r"```", 3.0),
            (r"\b(?:python|javascript|typescript|sql)\b", 2.0),
            (r"\b(?:function|method|variable|class)\b", 1.5),
            (r"\b(?:api|endpoint|middleware|repository)\b", 2.0),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.RELATIONSHIP: CategoryPattern(
        keywords=(
            "relationship", "partner", "boyfriend", "girlfriend", "spouse",
            "husband", "wife", "dating", "date", "marriage", "married",
            "breakup", "break up", "divorce", "cheating", "trust",
            "friend", "friendship", "family", "parent", "sibling",
            "love", "crush", "romantic", "toxic", "boundaries",
            "communication", "argument with my",
        ),
        patterns=(
            (r"\bmy (?:boyfriend|girlfriend|partner|spouse|husband|wife)\b", 3.0),
            (r"\b(?:breakup|break up|divorce|cheating)\b", 2.5),
            (r"\b(?:dating|relationship|marriage)\b", 2.0),
            (r"\bshould i (?:break up|leave|stay with)\b", 3.0),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.MEDICAL: CategoryPattern(
        keywords=(
            "symptom", "diagnosis", "disease", "medication", "medicine",
            "doctor", "physician", "hospital", "treatment", "therapy",
            "pain", "fever", "cough", "headache", "cancer", "diabetes",
            "depression", "anxiety disorder", "prescription", "dosage",
            "side effect", "health condition", "medical", "patient",
            "blood pressure", " cholesterol", "infection", "virus",
        ),
        patterns=(
            (r"\b(?:symptom|diagnos|prescrip)\w*\b", 2.5),
            (r"\b(?:medication|medicine|dosage|treatment)\b", 2.5),
            (r"\bshould i (?:see a|go to the) doctor\b", 3.0),
            (r"\b(?:side effect|adverse reaction)\b", 2.5),
            (r"\bis .+ (?:normal|dangerous|serious)\b.*(?:health|symptom|pain)", 2.0),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.BUSINESS: CategoryPattern(
        keywords=(
            "business", "startup", "company", "revenue", "profit", "loss",
            "investment", "investor", "market", "marketing", "sales",
            "strategy", "pricing", "customer", "client", "product",
            "saas", "b2b", "b2c", "valuation", "funding", "raise",
            "salary", "negotiate", "promotion", "career", "job offer",
            "entrepreneur", "competitor", "roi", "kpi", "margin",
        ),
        patterns=(
            (r"\b(?:startup|revenue|profit|valuation|funding)\b", 2.5),
            (r"\b(?:business model|go-to-market|market share)\b", 3.0),
            (r"\b(?:salary|job offer|promotion)\b.*(?:negotiat|accept|counter)", 2.5),
            (r"\b(?:roi|kpi|margin)\b", 2.0),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.POLITICS: CategoryPattern(
        keywords=(
            "politics", "political", "election", "vote", "voting", "campaign",
            "government", "policy", "legislation", "congress", "senate",
            "president", "democrat", "republican", "liberal", "conservative",
            "left wing", "right wing", "immigration", "tax policy",
            "geopolitics", "sanctions", "diplomacy", "parliament",
        ),
        patterns=(
            (r"\b(?:election|vote|voting|ballot)\b", 2.5),
            (r"\b(?:democrat|republican|liberal|conservative)\b", 2.5),
            (r"\b(?:government|policy|legislation|congress|senate)\b", 2.0),
            (r"\b(?:president|prime minister|parliament)\b", 2.0),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.EMOTION: CategoryPattern(
        keywords=(
            "feel", "feeling", "felt", "emotion", "emotional", "sad", "happy",
            "angry", "anxious", "anxiety", "stressed", "overwhelmed",
            "lonely", "frustrated", "depressed", "hopeless", "excited",
            "grateful", "guilty", "ashamed", "jealous", "hurt",
            "crying", "upset", "worried", "scared", "afraid",
            "mental health", "burnout", "exhausted",
        ),
        patterns=(
            (r"\bi (?:feel|felt|am feeling)\b", 3.0),
            (r"\bi(?:'m| am) (?:sad|happy|angry|anxious|stressed|depressed|lonely|scared)\b", 3.0),
            (r"\b(?:feeling|emotionally)\b", 2.0),
            (r"\b(?:overwhelmed|burned out|burnt out|exhausted)\b", 2.5),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.MATH: CategoryPattern(
        keywords=(
            "calculate", "compute", "solve", "equation", "formula",
            "integral", "derivative", "algebra", "geometry", "trigonometry",
            "probability", "statistics", "matrix", "vector", "logarithm",
            "percentage", "fraction", "polynomial", "theorem", "proof",
            "sum of", "product of", "square root", "factorial",
        ),
        patterns=(
            (r"\b(?:calculate|compute|solve)\b", 2.0),
            (r"\b\d+\s*[\+\-\*/\^]\s*\d+", 3.0),
            (r"\b(?:equation|integral|derivative|matrix|vector)\b", 2.5),
            (r"\b(?:percentage|fraction|ratio|probability)\b", 2.0),
            (r"\bwhat is \d+", 2.5),
            (r"\$\$.*\$\$", 2.5),
            (r"\\(?:frac|sum|int|sqrt)", 2.5),
        ),
        keyword_weight=1.5,
    ),
    InputCategory.GENERAL_CHAT: CategoryPattern(
        keywords=(
            "hello", "hi", "hey", "good morning", "good evening", "good night",
            "thanks", "thank you", "bye", "goodbye", "see you",
            "how are you", "what's up", "nice to meet", "help me",
            "tell me a joke", "who are you", "what can you do",
        ),
        patterns=(
            (r"^(?:hi|hello|hey|yo|sup)[\s!.?]*$", 3.0),
            (r"^(?:thanks|thank you|thx)[\s!.?]*$", 3.0),
            (r"\bhow are you\b", 2.5),
            (r"\b(?:good morning|good evening|good night)\b", 2.0),
            (r"\b(?:tell me a joke|who are you|what can you do)\b", 2.5),
        ),
        keyword_weight=1.0,
    ),
}


def compile_patterns() -> dict[InputCategory, list[tuple[re.Pattern[str], float]]]:
    """Pre-compile regex patterns for performance."""
    compiled: dict[InputCategory, list[tuple[re.Pattern[str], float]]] = {}
    for category, spec in CATEGORY_PATTERNS.items():
        compiled[category] = [
            (re.compile(pattern, re.IGNORECASE), weight)
            for pattern, weight in spec.patterns
        ]
    return compiled


COMPILED_PATTERNS = compile_patterns()
