from collections import defaultdict


VERDICT_CONFIRMED    = "CONFIRMED"
VERDICT_CONTRADICTED = "CONTRADICTED"
VERDICT_MIXED        = "MIXED"
VERDICT_UNVERIFIED   = "UNVERIFIED"

# 
VERDICT_SCORES = {
    VERDICT_CONFIRMED:    1.0,
    VERDICT_MIXED:        0.5,
    VERDICT_UNVERIFIED:   0.5,
    VERDICT_CONTRADICTED: 0.0,
}


def _aggregate_sentiments(analyzed_reviews: list[dict]) -> dict[str, dict]:
    """
    Collapses all per-review sentiment dicts into per-aspect sentiment counts
    and collects the review texts that mentioned each aspect.

    Input:
        analyzed_reviews: [
            {
                "review": "Great quality but arrived late",
                "aspect_and_sentiment": {"build_quality": "positive", "logistics": "negative"}
            },
            ...
        ]

    Output:
        {
            "build_quality": {
                "positive": 2, "negative": 0, "neutral": 0,
                "reviews": ["Great quality but arrived late", ...]
            },
            ...
        }
    
    The problem is that's organized by review. You need it organized by aspect, so you can answer "across all reviews,for example how did customers feel about build_quality?" That's what this function does.

    It loops through every review, validates the input, then for each aspect it increments the sentiment count and collects up to 3 example reviews — all grouped by aspect rather than by review.
    """
    counts = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "reviews": []})

    for entry in analyzed_reviews:
        if not isinstance(entry, dict):
            continue

        review_text          = entry.get("review", "")
        aspect_and_sentiment = entry.get("aspect_and_sentiment", {})

        if not isinstance(aspect_and_sentiment, dict):
            continue

        for aspect, sentiment in aspect_and_sentiment.items():
            if sentiment in ("positive", "negative", "neutral"):
                counts[aspect][sentiment] += 1
                # only store if under the cap AND this exact text isn't already stored
                if len(counts[aspect]["reviews"]) < 3 and review_text not in counts[aspect]["reviews"]:
                    counts[aspect]["reviews"].append(review_text)

    return dict(counts)


def _derive_verdict(sentiment_counts: dict, min_reviews: int = 2) -> str:
    """ 
    min_reviews = 2 is the minimum threshold. If fewer than 2 reviews mentioned an aspect, it returns UNVERIFIED regardless of sentiment. The 0.75 ratio is the majority threshold — one side needs 75% of the total positive + negative mentions to commit to a strong verdict.
    """

    pos   = sentiment_counts.get("positive", 0)
    neg   = sentiment_counts.get("negative", 0)
    total = pos + neg

    # not enough signal to make a confident call
    if total == 0:
        return VERDICT_UNVERIFIED
    if total < min_reviews:
        return VERDICT_UNVERIFIED

    # one side dominates (75%+) -> treat as confirmed or contradicted even if mixed
    if pos > 0 and neg == 0:
        return VERDICT_CONFIRMED
    if neg > 0 and pos == 0:
        return VERDICT_CONTRADICTED
    if pos / total >= 0.75:
        return VERDICT_CONFIRMED
    if neg / total >= 0.75:
        return VERDICT_CONTRADICTED
    return VERDICT_MIXED


def _compute_trust_score(results: list[dict]) -> int:
    verified = [r for r in results if r["verdict"] != VERDICT_UNVERIFIED]
    if not verified:
        return 50
    score = sum(VERDICT_SCORES[r["verdict"]] for r in verified) / len(verified)
    return round(score * 100)


def compare(claims: list[dict], analyzed_reviews: list[dict]) -> dict:
    """
    Main comparator function.

    Returns:
        {
            "trust_score": 72,
            "summary": {
                "confirmed": 3, "contradicted": 1, "mixed": 1, "unverified": 2
            },
            "results": [
                {
                    "aspect": "build_quality",
                    "claims": ["Made from 304 stainless steel"],
                    "verdict": "CONFIRMED",
                    "sentiment_counts": {"positive": 5, "negative": 1, "neutral": 0},
                    "sample_reviews": ["Great quality!", "Feels solid and well made"]
                },
                ...
            ],
            "unclaimed_aspects": [
                {
                    "aspect": "logistics",
                    "sentiment_counts": {"positive": 1, "negative": 3, "neutral": 0},
                    "sample_reviews": ["Arrived damaged", "Took 3 weeks to deliver"]
                },
                ...
            ]
        }
    """
    # group claims by aspect
    aspect_claims: dict[str, list[str]] = defaultdict(list)
    for item in claims:
        aspect = item.get("aspect")
        claim  = item.get("claim")
        if aspect and claim:
            aspect_claims[aspect].append(claim)

    sentiment_by_aspect = _aggregate_sentiments(analyzed_reviews)

    # --- claimed aspects: seller made at least one claim about this aspect ---
    results = []
    for aspect, claim_list in aspect_claims.items():
        counts  = sentiment_by_aspect.get(
            aspect, {"positive": 0, "negative": 0, "neutral": 0, "reviews": []}
        )
        verdict = _derive_verdict(counts)

        results.append({
            "aspect":           aspect,
            "claims":           claim_list,
            "verdict":          verdict,
            "sentiment_counts": {k: v for k, v in counts.items() if k != "reviews"},
            "sample_reviews":   counts.get("reviews", []),
        })

    results.sort(key=lambda r: list(VERDICT_SCORES.keys()).index(r["verdict"]))

    # --- unclaimed aspects: customers mentioned but seller never addressed 
    # NB: Unclaimed aspect with no review/sentiments are not displayed ---
    claimed_aspects   = set(aspect_claims.keys())
    unclaimed_aspects = []

    for aspect, counts in sentiment_by_aspect.items():
        if aspect in claimed_aspects:
            continue
        pos = counts.get("positive", 0)
        neg = counts.get("negative", 0)
        neu = counts.get("neutral", 0)
        if pos + neg + neu == 0:
            continue

        unclaimed_aspects.append({
            "aspect":           aspect,
            "sentiment_counts": {"positive": pos, "negative": neg, "neutral": neu},
            "sample_reviews":   counts.get("reviews", []),
        })

    # most negative first — highest risk to buyer surfaces at top
    unclaimed_aspects.sort(key=lambda u: u["sentiment_counts"]["negative"], reverse=True)

    trust_score = _compute_trust_score(results)

    summary = {
        "confirmed":    sum(1 for r in results if r["verdict"] == VERDICT_CONFIRMED),
        "contradicted": sum(1 for r in results if r["verdict"] == VERDICT_CONTRADICTED),
        "mixed":        sum(1 for r in results if r["verdict"] == VERDICT_MIXED),
        "unverified":   sum(1 for r in results if r["verdict"] == VERDICT_UNVERIFIED),
    }

    return {
        "trust_score":       trust_score,
        "summary":           summary,
        "results":           results,
        "unclaimed_aspects": unclaimed_aspects,
    }