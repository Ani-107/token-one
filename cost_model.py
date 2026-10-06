"""Token cost model for an AI feature (illustrative prices; verify current OpenAI pricing)."""

PRICE_IN = 2.50    # $ per 1M input tokens (illustrative)
PRICE_OUT = 10.00  # $ per 1M output tokens (illustrative)
PLAN_PRICE = 8.00  # $ per user per month


def cost(inp, out, reasoning=0, cached=0, cache_discount=0.5):
    """Cost of one request. Reasoning tokens bill as output. `cached` input tokens get a discount."""
    fresh = inp - cached
    in_cost = (fresh * PRICE_IN + cached * PRICE_IN * (1 - cache_discount)) / 1e6
    out_cost = (out + reasoning) * PRICE_OUT / 1e6
    return in_cost + out_cost


def chat(turns, first_in=1500, out=500, added_per_turn=700):
    """Chat history is resent every turn: input grows by (previous output + new user text)."""
    total, inp = 0.0, first_in
    for _ in range(turns):
        total += cost(inp, out)
        inp += added_per_turn
    return total


if __name__ == "__main__":
    base = cost(1500, 500)
    print(f"1. Base request (1,500 in / 500 out):      ${base:.5f}")
    print(f"2. 5-turn chat (history resent):           ${chat(5):.4f}  vs 5 independent ${5*base:.4f}  (+{chat(5)/(5*base)-1:.0%})")
    r = cost(1500, 500, reasoning=1500)
    print(f"3. With 1,500 hidden reasoning tokens:     ${r:.5f}  ({r/base:.1f}x base)")
    c = cost(1500, 500, cached=1300)
    print(f"4. With 1,300 tokens cached at 50% off:    ${c:.5f}  (-{1-c/base:.0%})")

    print("\nUser segments (monthly cost per user vs $8 plan):")
    segments = {
        "Typical": (40, 1500, 500),
        "Power":   (600, 4000, 500),
    }
    for name, (n, i, o) in segments.items():
        u = n * cost(i, o)
        print(f"  {name:8s} {n:4d} clicks  ${u:6.2f}  margin ${PLAN_PRICE - u:6.2f}")

    print("\nScale (all typical users):")
    for users in (10_000, 100_000, 1_000_000):
        print(f"  {users:>9,} users -> ${users * 40 * base:>10,.0f}/month")
