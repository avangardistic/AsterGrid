# Venue source page — Tick and lot size

- **URL:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size.md
- **Source class:** VENUE_PRIMARY_SOURCE
- **Retrieved:** 2026-09-20T18:35Z (built-in browser, `.md` raw variant)
- **Serves [HC]:** STR-0135, STR-0136, STR-0137, STR-0138, STR-0177
- **Hash note:** SHA-256 recorded in SOURCE_MANIFEST.md is of THIS saved extract file (faithful text of the fetched `.md`), not of an upstream byte stream.

## Verbatim excerpt

> # Tick and lot size
>
> Both Price (px) and Size (sz) have a maximum number of decimals that are accepted.
>
> Prices can have up to 5 significant figures, but no more than `MAX_DECIMALS - szDecimals` decimal places where `MAX_DECIMALS` is 6 for perps and 8 for spot. Integer prices are always allowed, regardless of the number of significant figures. E.g. `123456` is a valid price even though `12345.6` is not.
>
> Sizes are rounded to the `szDecimals` of that asset. For example, if `szDecimals = 3` then `1.001` is a valid size but `1.0001` is not.
>
> `szDecimals` for an asset is found in the meta response to the info endpoint
>
> ### Perp price examples
> `1234.5` is valid but `1234.56` is not (too many significant figures)
> `0.001234` is valid, but `0.0012345` is not (more than 6 decimal places)
> If `szDecimals = 1`, `0.01234` is valid but `0.012345` is not (more than `6 - szDecimals` decimal places)
>
> ### Signing
> Note that if implementing signing, trailing zeroes should be removed. See Signing for more details.

## Evidence status: VERIFIED

- STR-0135 — CONFIRMED verbatim: "Prices can have up to 5 significant figures, but no more than `MAX_DECIMALS - szDecimals` decimal places where `MAX_DECIMALS` is 6 for perps".
- STR-0136 — CONFIRMED verbatim: "Integer prices are always allowed, regardless of the number of significant figures."
- STR-0137 — CONFIRMED verbatim: "Sizes are rounded to the `szDecimals` of that asset … found in the meta response to the info endpoint."
- STR-0138 / STR-0177 — CONFIRMED (support): venue enforces the above and signing requires trailing-zero removal, so pre-sign normalization is required. (Strategy's "single most common third-party-SDK bug class" characterization is commentary, not a venue claim; the venue-verifiable part — precision rules + trailing-zero rule — is confirmed.)
- No mainnet/testnet difference stated for precision.
