# Prompt for research agent (any CLI agent): ASTER API grounding — Phase 0/P0b

**You are the Researcher.** Your output is **evidence files only** — no engine
code, no adapter code, no edits to `Strategy.md`, `prompt.md`, `src/`, or
`tests/`. Everything material goes into `research/aster/` as specified in
`research/aster/API_RESEARCH_ROADMAP.md` (W1–W6). Work in that order; W1/W2/W3/W5
need no credentials and can be completed in one session.

## Part 0 — Binding rules

1. **Fail-closed, evidence-or-silence.** Every claim carries: SOURCE class
   (`VENDOR_DOC`, `TESTNET_OBSERVATION`, `OWNER_DECISION`, `ASSUMPTION`),
   anchor (upstream path + line + fetch timestamp, or request/response pair),
   status (`VERIFIED` / `PARTIALLY_VERIFIED` / `UNVERIFIED` / `CONFLICTED`).
   A claim without an anchor is **deleted**, not kept.
2. **No vendoring.** Vendor docs stay upstream (`github.com/asterdex/api-docs`,
   manifest IDs S1–S4). Quote excerpts, cite paths + line numbers, record the
   upstream HEAD sha at fetch time. Never commit vendor files or their bulk.
3. **No secrets, ever.** No API-wallet private key, no signed payload, no
   testnet credential in any file, log, or fixture. The key lives only in the
   Owner's environment. Scripts you commit must read it from an env var and
   must have a `--dry-run` mode.
4. **Testnet only for probes (W6).** Mainnet access is read-only public
   endpoints only (e.g. funding history). No order on mainnet. Probe scripts
   default to the testnet base URL `https://fapi.asterdex-testnet.com` (F13).
5. **Do not decide owner questions.** OPEN-7 (CapitalBase field) and OPEN-10
   (write authorization for margin config) get a *proposal + evidence*, never a
   decision. Owner gates stay open until the Owner answers.
6. **Count with commands.** Every count in your report cites the command that
   produced it. Numbers without commands are not accepted.
7. **Stop conditions.** If the upstream docs contradict the contract delta
   (`docs/contract/CONTRACT_DELTA_ASTER.md`) on a material fact, or a doc
   section needed by a workstream does not exist: **stop that workstream**,
   record the conflict in `research/aster/CONFLICTS.md` (create if absent), and
   continue with the next workstream. Do not improvise a resolution.
8. **Repo safety:** work on a branch `research/aster-p0b`; before every commit,
   run `git status && git log --oneline -5 --all && git remote -v`; never
   rebase/amend pushed commits; do not push to `main`/`aster-migration` — push
   your branch and open a PR.

## Part 1 — Environment facts (record, then trust)

- Docs upstream: `asterdex/api-docs` @ master (re-fetch HEAD sha; compare
  against `eeddec8d97cd1250351f62b976973ae2a0d583c5` from the manifest; a moved
  HEAD is not a STOP — record it and re-anchor line numbers).
- V3 main doc: S3 `V3(Recommended)/EN/aster-finance-futures-api-v3.md`
  (~231 KB). Testnet doc: S4. Legacy (context only): S1, S2.
- Base URLs (F13/F14): mainnet REST `https://fapi.asterdex.com`; testnet REST
  `https://fapi.asterdex-testnet.com`; testnet WS `wss://fstream.asterdex-testnet.com`.
- Known weights: GET positionSide/dual = 30, GET positionRisk = 5 (F5/F10).
- Known error of interest: `-4225 Nonce Expired` (§6 of the contract delta).

## Part 2 — Workstreams

Execute W1 → W2 → W3 → W5 → W4 in that order (all doc-only), then W6 if and
only if the Owner has provided a testnet API wallet in the environment
(ask once; if absent, mark W6 `BLOCKED-ON-OWNER` in your report and stop).

Each workstream Wx is specified in full in
`research/aster/API_RESEARCH_ROADMAP.md` §1 — follow it exactly, including the
per-workstream Accept criteria and output filename. Summary:

| WS | Output file | Closes | Needs creds |
|---|---|---|---|
| W1 exchangeInfo/precision | `EXCHANGE_INFO.md` | §6.3 / OPEN-6a | no |
| W2 funding | `FUNDING_EVIDENCE.md` | §10 / OPEN-6b | no |
| W3 WS payloads | `WS_PAYLOADS.md` | manifest WS gap | no |
| W5 rate limits/errors | `RATE_LIMITS_ERRORS.md` | extends F15 | no |
| W4 account fields | `ACCOUNT_FIELDS.md` | OPEN-7 (proposal), OPEN-9 | no |
| W6 testnet probes | `TESTNET_PROBES.md` | OPEN-1, OPEN-4, OPEN-8 (+OPEN-9) | testnet wallet |

## Part 3 — Session protocol

1. **Before starting:** read `SOURCE_MANIFEST.md`, `CONTRACT_DELTA_ASTER.md`,
   `API_RESEARCH_ROADMAP.md`, and `ASTERGRID_HANDOFF.md`. Run
   `git fetch --all --prune && git status && git log --oneline -3 --all`.
2. **Per workstream:** fetch → extract → write evidence file → self-check
   against the Accept criteria → `git add research/aster/<file> && git commit`
   (one commit per workstream, message `research(P0b): W<n> <slug>`).
3. **Conflicts:** append to `research/aster/CONFLICTS.md`, never resolve.
4. **Final:** run the full-file self-audit (grep your own files for claims
   lacking anchors; delete or demote them), then write
   `research/aster/P0B_SESSION_REPORT.md`: workstreams done/blocked, OPEN-item
   status flips (with the flipping evidence anchor), conflicts, counts +
   commands, and the upstream HEAD sha used.

## Part 4 — Report format (final message)

1. Workstreams completed (with evidence-file paths) / blocked (reason).
2. OPEN items flipped: OPEN-6a, OPEN-6b, OPEN-7 (proposal only), OPEN-9,
   OPEN-1, OPEN-4, OPEN-8 — each with status and one-line evidence anchor.
3. Conflicts found (or "none").
4. Upstream docs HEAD sha at fetch time + drift vs manifest.
5. Commit hashes on your branch; PR URL.
6. Statement: "No secrets committed. No mainnet writes. No vendor files
   vendored. No owner gate decided."

## STOP list (summary)

Vendor contradiction with the contract delta on a material fact · required doc
section missing · any secret at risk of entering the repo · any mainnet write
attempt · any count without a command. **Fail-closed. Silence is never a
decision.**
