# Query Expansion Verification — Before/After

Author verification table of sample Indonesian tourism queries before and after
synonym expansion using the curated dictionary in
`backend/app/engine/query_expansion.py`. Each row shows the original query, the
expanded query, whether expansion occurred, and the synonyms added.

| # | Original query | Expanded query | Expansion? | Added synonyms |
|---|----------------|----------------|------------|----------------|
| 1 | curug bogor | curug bogor air terjun | Yes | air terjun |
| 2 | pantai bali | pantai bali bahari laut tepi laut | Yes | bahari, laut, tepi laut |
| 3 | penginapan bandung | penginapan bandung hotel losmen villa | Yes | hotel, losmen, villa |
| 4 | snorkeling lombok | snorkeling lombok selam menyelam | Yes | selam, menyelam |
| 5 | candi jogja | candi jogja situs bersejarah peninggalan sejarah | Yes | situs bersejarah, peninggalan sejarah |
| 6 | gunung bromo | gunung bromo puncak pegunungan | Yes | puncak, pegunungan |
| 7 | danau toba | danau toba telaga kolam danau | Yes | telaga, kolam danau |
| 8 | goa jomblang | goa jomblang gua guha | Yes | gua, guha |
| 9 | wisata pulau | wisata pulau pariwisata pelesir nusa selat | Yes | pariwisata, pelesir, nusa, selat |
| 10 | taman nasional | taman nasional taman taman wisata | Yes | taman, taman wisata |

Notes:
- Queries with no dictionary match return `has_expansion: false` and an unchanged
  expanded query (e.g. "xyzzy unknown term").
- Every synonym pair is stored bidirectionally, so expansion works regardless of
  which term in a pair appears in the user query.
- Multi-word dictionary entries (e.g. "air terjun", "situs bersejarah") are
  matched as contiguous spans in the query token stream.
