# Corpus Deduplication Verification Report

## 1. Executive Summary

- Target Category: Artikel Wisata Nusantara
- Similarity Threshold: > 95.0% text similarity
- Initial Raw Corpus Count: 700 documents
- Total Duplicates Detected & Removed: 57 documents
  - Exact Duplicates (Hash Collision): 19 documents
  - Near-Duplicates (>95% Similarity): 38 documents
- Final Clean Corpus Count: 643 unique documents
- Compliance Status: Verified (>= 500 unique documents requirement met)

## 2. Methodology & Detection Architecture

The deduplication engine implements a two-stage filter:

1. Exact Hash Matching: SHA-256 hash comparison across normalized text (case-folded, punctuation-stripped, and whitespace-collapsed). Identifies syndicated articles and verbatim reposts.
2. Near-Duplicate Matching: Blended character 5-gram Jaccard similarity (60% weight) and word-token Jaccard similarity (40% weight). Identifies articles with minor editorial edits, footer additions, or promotional CMS variations exceeding 0.95 similarity.

## 3. Sample Detected Duplicate Pairs

| No | Duplicate ID | Retained Primary ID | Similarity | Type | Title |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `wisata_raw_037` | `wisata_raw_036` | 0.9521 | near_duplicate | Pesona Wisata Alam Eksotis Curug Barong di Sentul |
| 2 | `wisata_raw_056` | `wisata_raw_055` | 0.9544 | near_duplicate | Harmoni Budaya dan Warisan Leluhur di Curug Awang Geopark Ciletuh |
| 3 | `wisata_raw_057` | `wisata_raw_055` | 0.9530 | near_duplicate | Harmoni Budaya dan Warisan Leluhur di Curug Sodong Geopark Ciletuh |
| 4 | `wisata_raw_084` | `wisata_raw_082` | 0.9538 | near_duplicate | Keindahan Tersembunyi Air Terjun Pulau Macan Kepulauan Seribu |
| 5 | `wisata_raw_132` | `wisata_raw_130` | 0.9529 | near_duplicate | Surga Snorkeling dan Keanekaragaman Hayati Laut di Pantai Padang Padang Badung & Kuta |
| 6 | `wisata_raw_201` | `wisata_raw_200` | 0.9574 | near_duplicate | Keindahan Tersembunyi Air Terjun Pulau Hoga Wakatobi Wakatobi & Buton |
| 7 | `wisata_raw_247` | `wisata_raw_246` | 0.9560 | near_duplicate | Eksotisme Pasir Putih dan Deburan Ombak Pantai Curug Sodong Geopark Ciletuh |
| 8 | `wisata_raw_318` | `wisata_raw_317` | 0.9556 | near_duplicate | Pesona Wisata Alam Eksotis Goa Tabuhan di Pacitan |
| 9 | `wisata_raw_339` | `wisata_raw_338` | 0.9512 | near_duplicate | Harmoni Budaya dan Warisan Leluhur di Danau Buyan Buleleng & Bali Utara |
| 10 | `wisata_raw_391` | `wisata_raw_390` | 0.9548 | near_duplicate | Keasrian Wisata Konservasi Hutan dan Satwa Liar di Pulau Hoga Wakatobi Wakatobi & Buton |
| 11 | `wisata_raw_417` | `wisata_raw_416` | 0.9517 | near_duplicate | Harmoni Budaya dan Warisan Leluhur di Curug Barong Sentul |
| 12 | `wisata_raw_436` | `wisata_raw_435` | 0.9520 | near_duplicate | Pesona Wisata Alam Eksotis Curug Awang di Geopark Ciletuh |
| 13 | `wisata_raw_437` | `wisata_raw_435` | 0.9506 | near_duplicate | Pesona Wisata Alam Eksotis Curug Sodong di Geopark Ciletuh |
| 14 | `wisata_raw_532` | `wisata_raw_530` | 0.9563 | near_duplicate | Surga Snorkeling dan Keanekaragaman Hayati Laut di Gili Air Lombok Barat & Gili |
| 15 | `wisata_raw_581` | `wisata_raw_580` | 0.9538 | near_duplicate | Menelusuri Jejak Sejarah dan Peninggalan Masa Lampau Pulau Hoga Wakatobi Wakatobi & Buton |
| 16 | `wisata_raw_611` | `wisata_raw_610` | 0.9576 | near_duplicate | Surga Snorkeling dan Keanekaragaman Hayati Laut di Telaga Warna Puncak & Cisarua |
| 17 | `wisata_raw_627` | `wisata_raw_626` | 0.9555 | near_duplicate | Sensasi Petualangan Trekking Menuju Puncak Curug Sodong Geopark Ciletuh |
| 18 | `wisata_raw_654` | `wisata_raw_650` | 0.9504 | near_duplicate | Surga Snorkeling dan Keanekaragaman Hayati Laut di Pulau Macan Kepulauan Seribu |
| 19 | `wisata_raw_661` | `wisata_raw_001` | 1.0000 | exact_hash | Pesona Keindahan Curug Leuwi Hejo Bogor |
| 20 | `wisata_raw_662` | `wisata_raw_003` | 1.0000 | exact_hash | Pesona Kawah Ratu dan Gunung Tangkuban Parahu Bandung |
| 21 | `wisata_raw_663` | `wisata_raw_005` | 1.0000 | exact_hash | Keindahan Tebing Karang Pantai Sawarna Lebak Banten |
| 22 | `wisata_raw_664` | `wisata_raw_007` | 1.0000 | exact_hash | Kemegahan Kawah Putih Ciwidey Danau Belerang Eksotis Bandung |
| 23 | `wisata_raw_665` | `wisata_raw_009` | 1.0000 | exact_hash | Petualangan Menyusuri Aliran Sungai Green Canyon Pangandaran |
| 24 | `wisata_raw_666` | `wisata_raw_011` | 1.0000 | exact_hash | Pesona Curug Nangka di Kaki Gunung Salak Bogor |
| 25 | `wisata_raw_667` | `wisata_raw_013` | 1.0000 | exact_hash | Keindahan Karang Bolong Pantai Anyer Serang Banten |

## 4. Verification Conclusion

All 57 duplicate documents were isolated from the production corpus. The clean corpus containing 643 unique documents is saved in `data/processed/corpus_clean.json` and `data/processed/corpus_clean.csv` for indexing and retrieval evaluation.
