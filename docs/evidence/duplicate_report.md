# Corpus Deduplication Verification Report

## 1. Executive Summary

- Target Category: Artikel Wisata Nusantara
- Similarity Threshold: > 95.0% text similarity
- Initial Raw Corpus Count: 700 documents
- Total Duplicates Detected & Removed: 51 documents
  - Exact Duplicates (Hash Collision): 20 documents
  - Near-Duplicates (>95% Similarity): 31 documents
- Final Clean Corpus Count: 649 unique documents
- Compliance Status: Verified (>= 500 unique documents requirement met)

## 2. Methodology & Detection Architecture

The deduplication engine implements a two-stage filter:

1. Exact Hash Matching: SHA-256 hash comparison across normalized text (case-folded, punctuation-stripped, and whitespace-collapsed). Identifies syndicated articles and verbatim reposts.
2. Near-Duplicate Matching: Blended character 5-gram Jaccard similarity (60% weight) and word-token Jaccard similarity (40% weight). Identifies articles with minor editorial edits, footer additions, or promotional CMS variations exceeding 0.95 similarity.

## 3. Sample Detected Duplicate Pairs

| No | Duplicate ID | Retained Primary ID | Similarity | Type | Title |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `wisata_raw_145` | `wisata_raw_143` | 0.9538 | near_duplicate | Keindahan Tersembunyi Air Terjun Pulau Macan Kepulauan Seribu |
| 2 | `wisata_raw_185` | `wisata_raw_184` | 0.9502 | near_duplicate | Pesona Wisata Alam Eksotis Coban Talun di Bromo & Semeru |
| 3 | `wisata_raw_275` | `wisata_raw_274` | 0.9511 | near_duplicate | Keindahan Tersembunyi Air Terjun Pulau Hoga Wakatobi & Buton |
| 4 | `wisata_raw_331` | `wisata_raw_330` | 0.9568 | near_duplicate | Eksotisme Pasir Putih dan Deburan Ombak Pantai Sodong Geopark Ciletuh |
| 5 | `wisata_raw_383` | `wisata_raw_381` | 0.9514 | near_duplicate | Surga Snorkeling dan Keanekaragaman Hayati Laut di Jomblang Gunungkidul |
| 6 | `wisata_raw_384` | `wisata_raw_382` | 0.9529 | near_duplicate | Surga Snorkeling dan Keanekaragaman Hayati Laut di Ngobaran Gunungkidul |
| 7 | `wisata_raw_462` | `wisata_raw_458` | 0.9503 | near_duplicate | Keindahan Tersembunyi Air Terjun Tuk Tuk Danau Toba & Karo |
| 8 | `wisata_raw_598` | `wisata_raw_596` | 0.9559 | near_duplicate | Keindahan Tersembunyi Air Terjun Jomblang Gunungkidul |
| 9 | `wisata_raw_599` | `wisata_raw_597` | 0.9545 | near_duplicate | Keindahan Tersembunyi Air Terjun Ngobaran Gunungkidul |
| 10 | `wisata_raw_644` | `wisata_raw_641` | 0.9502 | near_duplicate | Keindahan Tersembunyi Air Terjun Diamond Beach Nusa Penida & Lembongan |
| 11 | `wisata_raw_653` | `wisata_raw_651` | 0.9563 | near_duplicate | Surga Snorkeling dan Keanekaragaman Hayati Laut di Gili Air Lombok Barat & Gili |
| 12 | `wisata_raw_661` | `wisata_raw_001` | 1.0000 | exact_hash | Pesona Keindahan Curug Leuwi Hejo Bogor |
| 13 | `wisata_raw_662` | `wisata_raw_003` | 1.0000 | exact_hash | Pesona Kawah Ratu dan Gunung Tangkuban Parahu Bandung |
| 14 | `wisata_raw_663` | `wisata_raw_005` | 1.0000 | exact_hash | Keindahan Tebing Karang Pantai Sawarna Lebak Banten |
| 15 | `wisata_raw_664` | `wisata_raw_007` | 1.0000 | exact_hash | Kemegahan Kawah Putih Ciwidey Danau Belerang Eksotis Bandung |
| 16 | `wisata_raw_665` | `wisata_raw_009` | 1.0000 | exact_hash | Petualangan Menyusuri Aliran Sungai Green Canyon Pangandaran |
| 17 | `wisata_raw_666` | `wisata_raw_011` | 1.0000 | exact_hash | Pesona Curug Nangka di Kaki Gunung Salak Bogor |
| 18 | `wisata_raw_667` | `wisata_raw_013` | 1.0000 | exact_hash | Eksotisme Air Terjun Megah Curug Cimahi Bandung |
| 19 | `wisata_raw_668` | `wisata_raw_015` | 1.0000 | exact_hash | Keajaiban Danau Vulkanik Kawah Talaga Bodas Garut |
| 20 | `wisata_raw_669` | `wisata_raw_017` | 1.0000 | exact_hash | Pemandangan Gunung Gede Pangrango dari Telaga Saat Puncak |
| 21 | `wisata_raw_670` | `wisata_raw_019` | 1.0000 | exact_hash | Keindahan Alami Air Terjun Curug Luhur Pangandaran |
| 22 | `wisata_raw_671` | `wisata_raw_021` | 1.0000 | exact_hash | Eksotisme Pasir Putih Pantai Kuta Bali |
| 23 | `wisata_raw_672` | `wisata_raw_023` | 1.0000 | exact_hash | Eksplorasi Satwa Purba di Taman Nasional Komodo NTT |
| 24 | `wisata_raw_673` | `wisata_raw_025` | 1.0000 | exact_hash | Misteri Danau Tiga Warna di Kawah Gunung Kelimutu Flores |
| 25 | `wisata_raw_674` | `wisata_raw_027` | 1.0000 | exact_hash | Keindahan Bukit Teletubbies dan Pantai Pasir Putih Nusa Penida |

## 4. Verification Conclusion

All 51 duplicate documents were isolated from the production corpus. The clean corpus containing 649 unique documents is saved in `data/processed/corpus_clean.json` and `data/processed/corpus_clean.csv` for indexing and retrieval evaluation.
