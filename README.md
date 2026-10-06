# Token cost case study: what happens inside an OpenAI model

When you add an AI feature, one click looks like it costs almost nothing. This case study follows **one request** from the click to the invoice, explains **why each step costs what it does**, and shows how a cheap-looking request becomes a margin problem at scale.

**Scenario:** a note-taking app that costs **$8/month** has an "AI summarize" button. A user clicks it on a meeting note, and the app calls an OpenAI model.

> Prices are illustrative: **$2.50 per 1M input tokens, $10 per 1M output tokens**. Always verify current OpenAI pricing and caching rules before using these numbers. Mechanism explanations are simplified for teaching.

## What's inside
| Path | What it is |
|---|---|
| `docs/concepts.md` | Every concept explained in plain language, with analogies (start here if terms are new) |
| `docs/case-study.md` | The full written case study with every step and table |
| `cost_model.py` | A small Python model that reproduces every number below |
| `web/index.html` | Interactive explainer with a live cost calculator (open in a browser) |
| `images/` | The diagrams used in this README |

## 1. Life of one click
![Life of one AI summarize click](images/01-request-lifecycle.svg)

**What the picture shows, left to right:**
1. **The app builds the prompt.** The model is sent more than the user's click: your hidden rules (300 tokens), the meeting note (1,000) and the user's instruction (200). That is **1,500 input tokens**, and you pay for all of them.
2. **The tokenizer splits the text.** Models read small pieces called tokens, roughly 4 characters each, not words. Tokens are the unit on the invoice.
3. **The model reads all the input at once.** This is called *prefill*.
4. **The model writes the answer one token at a time.** This is called *decode*. A 500-token summary takes 500 rounds.
5. **The invoice:** $0.00375 for input plus $0.00500 for output, **$0.00875 per click**.

## 2. Why output costs more than input
![Prefill versus decode](images/02-prefill-vs-decode.svg)

**Left, prefill:** all 1,500 input tokens go through the model in one parallel pass. Parallel work uses hardware efficiently, so each token is cheap.

**Right, decode:** the model predicts one token, adds it to the text, then predicts the next. Each token needs the one before it, so it cannot be done all at once. 500 tokens means 500 rounds.

**Takeaway:** output is slower for the user and pricier for you. Long answers hurt both latency and cost.

## 3. Why conversations get expensive
![Chat history growth](images/03-chat-history-growth.svg)

The API has no memory between calls. To continue a chat ("make it shorter", "add action items"), your app resends the earlier messages every time, so the **input grows each turn** (green bars) while the output stays about the same (orange).

Over 5 turns the model reads 14,500 input tokens instead of 7,500. Cost: **$0.061 versus $0.044**, about **40% more**, with no new feature shipped. This is often called *context creep*.

## 4. How choices change the bill
![Cost scenarios](images/04-cost-scenarios.svg)

- **Base:** $0.00875 per click.
- **Prompt caching:** if the start of the prompt is identical across requests (your rules, a shared document), those tokens can be billed at a discount. With 1,300 of 1,500 tokens cached at 50% off, cost falls about **19%**. Discount size and rules vary by model, so check the docs.
- **Reasoning models:** they think in hidden tokens before answering. You never see them, but they are billed as output. 1,500 hidden tokens make the same click about **2.7x** more expensive.

## 5. From one click to a business decision
| User | Clicks/month | Tokens per click | Cost per user | Margin on $8 plan |
|---|---|---|---|---|
| Typical | 40 | 1,500 in / 500 out | $0.35 | +$7.65 |
| Power user | 600 | 4,000 in / 500 out | $9.00 | **-$1.00** |

Averages hide the people who decide your margin. Model the distribution of users, then pick levers: route simple requests to a smaller model, cap output length, cache the stable prompt prefix, trim history, or meter heavy usage. Each has a quality trade-off, covered in `docs/case-study.md`.

## Run the model
```bash
python3 cost_model.py
```
No dependencies. Edit the constants at the top to try your own prices and usage.

## Key takeaways
- You pay per token, in and out, and output costs more.
- Everything you send is billed, including rules and chat history.
- Hidden reasoning tokens count as output.
- Cached prompts can give some cost back.
- Average cost hides heavy users.

## License
Add a license of your choice (e.g. MIT) before publishing.
