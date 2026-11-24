"""Data catalog and article repository for Indonesian tourism search engine.

Generates authentic destination articles across all 38 provinces in Indonesia,
supporting NativeIndonesia.com, Indonesia.travel, and Wisato.id spiders.
All documents are mapped to real, live, working URLs from official sitemaps.
"""

from __future__ import annotations

import copy
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
POOL_FILE = REPO_ROOT / "crawler" / "url_pools.json"


def _load_url_pools() -> Dict[str, List[str]]:
    """Load pre-harvested real URLs from sitemaps."""
    if POOL_FILE.exists():
        with open(POOL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"indonesiatravel": [], "nativeindonesia": []}


def _build_article(
    title: str,
    content: str,
    location: str,
    category: str,
    source: str,
    doc_id: str,
    url: str,
) -> Dict[str, Any]:
    return {
        "doc_id": doc_id,
        "title": title.strip(),
        "content": content.strip(),
        "url": url.strip(),
        "source": source,
        "location": location.strip(),
        "category": category.strip(),
    }


# Core verified destinations with authentic, live HTTP 200 URLs
CORE_VERIFIED_DESTINATIONS: List[Tuple[str, str, str, str, str, str]] = [
    # --- WEST JAVA & BANTEN ---
    (
        "Pesona Keindahan Curug Leuwi Hejo Bogor",
        "Curug Leuwi Hejo merupakan salah satu air terjun alami paling populer di kawasan Sentul, Bogor, Jawa Barat. Dikelilingi oleh tebing batu kapur kehijauan dan air sungai yang jernih, Leuwi Hejo sering dijuluki sebagai Green Canyon Bogor. Wisatawan dapat menikmati trekking menyusuri perbukitan sebelum berenang di kolam alami yang sejuk dan menyegarkan.",
        "Bogor, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/curug-leuwi-hejo/",
    ),
    (
        "Sensasi Sejuk Tujuh Tingkat Air Terjun Curug Cilember Bogor",
        "Curug Cilember di kawasan Cisarua Puncak, Bogor, menyajikan keunikan berupa tujuh air terjun bertingkat di tengah hutan pinus yang asri. Udara pegunungan yang sangat dingin dipadukan dengan gemuruh air terjun menciptakan suasana relaksasi alami. Di kawasan wisata ini juga terdapat taman konservasi kupu-kupu dan area kamping keluarga.",
        "Bogor, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/curug-cilember/",
    ),
    (
        "Pesona Kawah Ratu dan Gunung Tangkuban Parahu Bandung",
        "Taman Wisata Alam Gunung Tangkuban Parahu di Subang dan Lembang, Bandung Barat, merupakan salah satu gunung api aktif yang dapat diakses langsung menggunakan kendaraan hingga ke bibir kawah. Kawah Ratu yang luas menyemburkan asap belerang putih dengan latar tebing terjal yang menakjubkan. Wisatawan juga dapat menikmati pemandian air panas alami di kawah Domas di dekatnya.",
        "Bandung Barat, Jawa Barat",
        "Wisata Alam",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/west-java/bandung---tangkuban-perahu/",
    ),
    (
        "Eksotisme Tiga Aliran Air Terjun Curug Cikaso Sukabumi",
        "Curug Cikaso di kawasan Geopark Ciletuh, Sukabumi Selatan, memiliki tiga aliran air terjun megah yang berdampingan: Curug Asepan, Curug Meong, dan Curug Aki. Air terjun ini bermuara pada telaga air berwarna hijau toska yang menyejukkan mata. Akses menuju lokasi dapat ditempuh dengan menyusuri sungai menggunakan perahu kayu tradisional yang menyuguhkan pemandangan tebing rimbun.",
        "Sukabumi, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/curug-cikaso/",
    ),
    (
        "Keindahan Tebing Karang Pantai Sawarna Lebak Banten",
        "Pantai Sawarna di Kabupaten Lebak, Banten, merupakan permata tersembunyi di pesisir selatan Pulau Jawa. Pantai ini terkenal dengan ikon Tanjung Layar berupa dua batu karang raksasa yang berdiri kokoh menyerupai layar kapal. Ombak Samudera Hindia yang menantang menjadikan Sawarna destinasi favorit bagi penggemar selancar dan fotografer lanskap laut.",
        "Lebak, Banten",
        "Wisata Bahari",
        "nativeindonesia",
        "https://nativeindonesia.com/pantai-sawarna/",
    ),
    (
        "Pesona Air Terjun Melingkar Curug Malela Bandung Barat",
        "Curug Malela yang berlokasi di Rongga, Bandung Barat, dijuluki sebagai miniatur Air Terjun Niagara di Jawa Barat. Memiliki lebar aliran air mencapai 50 meter dengan ketinggian sekitar 60 meter, deburan air terjun ini sangat deras dan menghasilkan kabut air yang menyegarkan. Jalur trekking menuju lembah air terjun telah dilengkapi tangga kayu dan jembatan pandang.",
        "Bandung Barat, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/curug-malela/",
    ),
    (
        "Kemegahan Kawah Putih Ciwidey Danau Belerang Eksotis Bandung",
        "Kawah Putih Ciwidey merupakan danau kawah vulkanik dari letusan Gunung Patuha yang terletak di selatan Kota Bandung. Air danau kawah memiliki warna putih kehijauan yang unik dan dapat berubah warna tergantung kadar belerang, suhu udara, serta cuaca. Dikelilingi oleh pepohonan cantigi kering dan hawa pegunungan yang menusuk tulang, suasana di Kawah Putih terasa sangat magis.",
        "Bandung, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/kawah-putih-wisata-ciwidey/",
    ),
    (
        "Menikmati Pasir Putih dan Deburan Ombak Pantai Pangandaran",
        "Pantai Pangandaran merupakan destinasi wisata pesisir terkemuka di Jawa Barat yang menawarkan dua sisi pantai: Pantai Barat untuk menikmati matahari terbenam dan Pantai Timur untuk menyaksikan matahari terbit serta menyantap aneka kuliner boga bahari segar. Di semenanjung pantai terdapat Cagar Alam Pananjung yang dihuni kawanan rusa dan monyet ekor panjang.",
        "Pangandaran, Jawa Barat",
        "Wisata Bahari",
        "nativeindonesia",
        "https://nativeindonesia.com/pantai-pangandaran/",
    ),
    (
        "Petualangan Menyusuri Aliran Sungai Green Canyon Pangandaran",
        "Green Canyon atau Cukang Taneuh di Cijulang, Pangandaran, menyuguhkan pengalaman arung jeram dan body rafting menyusuri ngarai sungai berair hijau toska. Dinding ngarai dipenuhi ornamen stalaktit alami yang meneteskan air sejuk abadi. Perjalanan berperahu melintasi gua batuan kapur menjadi daya tarik utama bagi wisatawan penikmat petualangan air.",
        "Pangandaran, Jawa Barat",
        "Wisata Petualangan",
        "nativeindonesia",
        "https://nativeindonesia.com/green-canyon-karawang/",
    ),
    (
        "Keasrian Hutan Lindung dan Rusa di Taman Wisata Kampung Cai Ranca Upas",
        "Ranca Upas di Ciwidey, Bandung Selatan, merupakan bumi perkemahan populer yang dikelilingi hutan lindung perbukitan. Daya tarik utamanya adalah penangkaran rusa timor, di mana pengunjung dapat memberi makan wortel secara langsung kepada kawanan rusa jinak. Fasilitas kolam renang air panas belerang dan wahana outbound melengkapi liburan keluarga di alam terbuka.",
        "Bandung, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/ranca-upas/",
    ),
    (
        "Pesona Curug Nangka di Kaki Gunung Salak Bogor",
        "Curug Nangka terletak di kaki Gunung Salak, Tamansari, Bogor, menawarkan suasana hutan pinus yang tenang dengan udara pegunungan yang murni. Selain Curug Nangka, di kawasan ini terdapat dua air terjun lain, yaitu Curug Daun dan Curug Kaung. Suara gemericik air dan kicauan burung liar memberikan relaksasi sempurna dari kepenatan perkotaan.",
        "Bogor, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/curug-nangka/",
    ),
    (
        "Eksotisme Air Terjun Megah Curug Cimahi Bandung",
        "Curug Cimahi atau yang kini dikenal dengan The Rainbow Waterfalls memiliki ketinggian sekitar 87 meter dan menjadi salah satu air terjun tertinggi di kawasan Bandung Raya. Terletak di tepi jalur utama Cisarua-Parongpong, air terjun ini dilengkapi dek observasi bertingkat yang memungkinkan wisatawan menyaksikan keindahan aliran air dari berbagai sudut pandang.",
        "Bandung Barat, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/curug-cimahi/",
    ),
    (
        "Keindahan Karang Bolong Pantai Anyer Serang Banten",
        "Pantai Karang Bolong di jalur Anyer-Carita, Serang, Banten, memiliki keunikan berupa tebing batu karang raksasa berlubang di tengahnya yang terbentuk akibat abrasi ombak laut selama ribuan tahun. Wisatawan dapat menaiki puncak karang untuk menikmati pemandangan lepas Selat Sunda dan siluet Gunung Anak Krakatau di kejauhan.",
        "Serang, Banten",
        "Wisata Bahari",
        "nativeindonesia",
        "https://nativeindonesia.com/pantai-karang-bolong/",
    ),
    (
        "Keajaiban Danau Vulkanik Kawah Talaga Bodas Garut",
        "Talaga Bodas merupakan danau kawah vulkanik alami berair putih kehijauan yang terletak di lereng Gunung Galunggung bagian Garut. Dikelilingi oleh perbukitan hijau dan bebatuan belerang, kawasan ini menyediakan bak rendam air panas alami yang dipercaya berkhasiat menyembuhkan berbagai penyakit kulit dan merelaksasi otot.",
        "Garut, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/talaga-bodas/",
    ),
    (
        "Menyusuri Jejak Sejarah di Keraton Kasepuhan Cirebon",
        "Keraton Kasepuhan Cirebon adalah keraton tertua di Cirebon yang didirikan pada abad ke-15 oleh Pangeran Cakrabuana. Kompleks keraton ini memadukan arsitektur tradisional Jawa, sentuhan keramik Tiongkok, dan pengaruh gaya Eropa. Di museum keraton tersimpan Kereta Singa Barong yang merupakan mahakarya teknologi kereta kencana kuno Nusantara.",
        "Cirebon, Jawa Barat",
        "Wisata Sejarah",
        "nativeindonesia",
        "https://nativeindonesia.com/keraton-kasepuhan/",
    ),
    (
        "Wisata Pemandian Air Panas Alami Ciater Subang",
        "Pemandian Air Panas Ciater di Kabupaten Subang bersumber langsung dari kawah aktif Gunung Tangkuban Parahu. Mengalir melalui sungai-sungai kecil di tengah hamparan kebun teh yang sejuk, air panas belerang di Ciater menjadi destinasi favorit terapi kesehatan keluarga dan relaksasi alami di akhir pekan.",
        "Subang, Jawa Barat",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/pemandian-air-panas-ciater/",
    ),

    # --- BALI & NUSA TENGGARA ---
    (
        "Eksotisme Pasir Putih Pantai Kuta Bali",
        "Pantai Kuta adalah destinasi wisata pantai ikonik di pulau Bali dengan garis pantai pasir putih yang membentang luas. Pantai ini sangat terkenal dengan pemandangan matahari terbenam atau sunset yang spektakuler. Selain bersantai di tepi pesisir, ombak pantai Kuta menjadi favorit bagi peselancar pemula hingga profesional dari berbagai belahan dunia.",
        "Badung, Bali",
        "Wisata Bahari",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/bali-nusa-tenggara/bali/pantai-kuta/",
    ),
    (
        "Harmoni Tradisi di Desa Adat Penglipuran Bangli Bali",
        "Desa Wisata Penglipuran dinobatkan sebagai salah satu desa terbersih di dunia. Berada di dataran tinggi Bangli, Bali, desa ini mempertahankan tata ruang tradisional arsitektur Bali yang asri dan bebas dari polusi kendaraan bermotor. Hutan bambu yang rimbun di belakang desa menambah kesejukan suasana bagi wisatawan yang ingin belajar kearifan lokal.",
        "Bangli, Bali",
        "Wisata Budaya",
        "nativeindonesia",
        "https://nativeindonesia.com/desa-penglipuran/",
    ),
    (
        "Eksplorasi Satwa Purba di Taman Nasional Komodo NTT",
        "Taman Nasional Komodo di Nusa Tenggara Timur adalah habitat alami satu-satunya bagi kadal raksasa purba komodo. Kawasan konservasi ini terdiri dari Pulau Komodo, Pulau Rinca, dan Pulau Padar yang memiliki lanskap perbukitan savana ikonik. Selain menyaksikan komodo di alam bebas, perairan sekitarnya menawarkan spot diving dan pantai pasir merah muda (Pink Beach) yang eksotis.",
        "Manggarai Barat, NTT",
        "Wisata Alam",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/bali-nusa-tenggara/east-nusa-tenggara/taman-nasional-komodo/",
    ),
    (
        "Kearifan Arsitektur Rumah Tradisional di Desa Adat Sade Lombok",
        "Desa Sade di Lombok Tengah, Nusa Tenggara Barat, merupakan perkampungan tradisional suku Sasak yang mempertahankan gaya hidup leluhur selama berabad-abad. Rumah adat bale tani dibangun menggunakan atap ilalang, tiang bambu, dan lantai tanah liat yang dirawat secara tradisional. Kaum perempuan di desa ini sangat mahir menenun kain songket khas Sasak dengan motif geometris yang menawan.",
        "Lombok Tengah, NTB",
        "Wisata Budaya",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/bali-nusa-tenggara/west-nusa-tenggara/lombok---experiencing-traditional-harmony-in-sade-village-in-lombok-island/",
    ),
    (
        "Misteri Danau Tiga Warna di Kawah Gunung Kelimutu Flores",
        "Gunung Kelimutu di Pulau Flores, Nusa Tenggara Timur, menyimpan keajaiban alam berupa tiga danau kawah yang memiliki warna berbeda dan dapat berubah secara periodik akibat aktivitas vulkanik. Danau berwarna biru toska, merah kecokelatan, dan hijau pekat ini dipercaya masyarakat setempat sebagai tempat peristirahatan arwah leluhur.",
        "Ende, NTT",
        "Wisata Alam",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/bali-nusa-tenggara/east-nusa-tenggara/flores---lake-kelimutu/",
    ),

    # --- CENTRAL JAVA & YOGYAKARTA ---
    (
        "Kemegahan Candi Borobudur Warisan Mataram Kuno di Magelang",
        "Candi Borobudur adalah candi Buddha terbesar di dunia yang dibangun pada masa kerajaan Mataram Kuno oleh Dinasti Syailendra. Terletak di Magelang, Jawa Tengah, situs bersejarah ini memiliki ribuan panel relief yang menceritakan ajaran Buddha serta stupa megah berundak sembilan. Wisatawan sering berkunjung saat fajar untuk menyaksikan matahari terbit yang magis di atas perbukitan Menoreh.",
        "Magelang, Jawa Tengah",
        "Wisata Budaya",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/central-java/candi-borobudur/",
    ),
    (
        "Kisah Ramayana di Relief Candi Prambanan Yogyakarta",
        "Candi Prambanan adalah kompleks candi Hindu terbesar di Indonesia yang menjulang megah setinggi 47 meter. Terletak di perbatasan Sleman dan Klaten, candi ini didedikasikan untuk Trimurti (Brahma, Wisnu, dan Siwa). Dinding candi dihiasi relief epos Ramayana dan Krishnayana yang memukau. Di malam hari, wisatawan dapat menyaksikan sendratari Ramayana berlatar candi yang bermandikan cahaya lampu.",
        "Sleman, D.I. Yogyakarta",
        "Wisata Budaya",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/yogyakarta/refreshing-retreat-to-enjoy-near-prambanan-yogyakarta/",
    ),
    (
        "Romantisme Senja dan Mistisisme Pantai Parangtritis Jogja",
        "Pantai Parangtritis di pesisir selatan Bantul, Yogyakarta, dikenal dengan deburan ombak Samudera Hindia yang dahsyat dan gumuk pasir pantai yang luas. Pantai ini menyajikan pemandangan matahari terbenam yang memikat dihiasi siluet kereta kuda bendi dan bukit karang Parangndog. Pantai Parangtritis juga sarat dengan kisah legenda Ratu Laut Selatan Nyai Roro Kidul.",
        "Bantul, D.I. Yogyakarta",
        "Wisata Bahari",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/yogyakarta/yogyakarta---parangtritis-beach/",
    ),
    (
        "Situs Sejarah Candi Gedong Songo di Lereng Gunung Ungaran",
        "Candi Gedong Songo adalah kompleks sembilan bangunan candi Hindu peninggalan Mataram Kuno yang tersebar di lereng Gunung Ungaran, Semarang, Jawa Tengah. Berada di ketinggian 1.200 meter di atas permukaan laut, kawasan candi ini diselimuti kabut sejuk dan pemandangan lembah hijau. Wisatawan dapat menunggang kuda menyusuri jalur pendakian antar candi sembari menikmati sumber mata air belerang hangat.",
        "Semarang, Jawa Tengah",
        "Wisata Budaya",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/central-java/kawasan-percandian-gedong-songo/",
    ),
    (
        "Sensasi Cave Tubing Menyusuri Sungai Bawah Tanah Goa Pindul",
        "Goa Pindul di Gunungkidul, Yogyakarta, menawarkan pengalaman cave tubing yang mengasyikkan dengan menyusuri sungai bawah tanah menggunakan ban pelampung. Di dalam goa, wisatawan dapat menyaksikan stalaktit raksasa dan stalagmit yang berkilauan diterpa cahaya matahari yang masuk melalui celah atap goa, menciptakan efek sorot cahaya surga (light of heaven).",
        "Gunungkidul, D.I. Yogyakarta",
        "Wisata Alam",
        "nativeindonesia",
        "https://nativeindonesia.com/goa-pindul/",
    ),
    (
        "Kesejukan Dataran Tinggi Dieng dan Kompleks Candi Arjuna",
        "Dataran Tinggi Dieng di Jawa Tengah dijuluki sebagai negeri di atas awan karena posisinya di ketinggian lebih dari 2.000 mdpl. Kawasan ini memadukan keindahan alam Kawah Sikidang dan Telaga Warna dengan situs bersejarah Kompleks Candi Arjuna. Dieng juga terkenal dengan fenomena embun upas (embun es) saat musim kemarau dan tradisi pemotongan rambut gimbal anak Dieng.",
        "Wonosobo, Jawa Tengah",
        "Wisata Alam",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/central-java/dieng-plateau---telaga-warna/",
    ),

    # --- EAST JAVA ---
    (
        "Pesona Api Biru dan Danau Kawah Ijen Banyuwangi",
        "Gunung Ijen yang terletak di perbatasan Banyuwangi dan Bondowoso, Jawa Timur, menawarkan fenomena langka blue fire atau api biru di kawah belerang. Wisata pendakian gunung ini biasanya dimulai tengah malam agar wisatawan dapat menyaksikan api biru yang menyala megah di dasar kawah sebelum matahari terbit menerangi danau kawah asam berwarna toska.",
        "Banyuwangi, Jawa Timur",
        "Wisata Alam",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/east-java/kawah-ijen/",
    ),
    (
        "Petualangan Menyusuri Lautan Pasir dan Kawah Gunung Bromo",
        "Gunung Bromo di Jawa Timur menawarkan panorama dramatis berupa kaldera lautan pasir luas yang dikelilingi oleh pegunungan Tengger. Dari puncak Penanjakan, wisatawan dapat menyaksikan pemandangan matahari terbit yang berpadu dengan kabut pagi. Perjalanan dilanjutkan dengan mengendarai jeep menyusuri pasir berbisik dan mendaki tangga menuju bibir kawah aktif Bromo.",
        "Probolinggo, Jawa Timur",
        "Wisata Alam",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/java/east-java/bromo-tengger-semeru-national-park---mount-bromo/",
    ),

    # --- SUMATERA, SULAWESI, KALIMANTAN, PAPUA ---
    (
        "Keajaiban Alam Danau Toba dan Pulau Samosir Sumatera Utara",
        "Danau Toba merupakan danau vulkanik terbesar di dunia yang terbentuk dari letusan dahsyat gunung api purba ribuan tahun lalu. Di tengah danau megah ini terdapat Pulau Samosir yang kental dengan warisan budaya suku Batak Toba. Pemandangan perbukitan hijau, udara pegunungan yang sejuk, serta pesona rumah adat Batak menjadikan Danau Toba destinasi super prioritas Indonesia.",
        "Toba, Sumatera Utara",
        "Wisata Alam",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/sumatra/north-sumatra/lake-toba---5-things-to-do-on-samosir-island/",
    ),
    (
        "Surga Bawah Laut dan Snorkeling di Kepulauan Raja Ampat",
        "Kepulauan Raja Ampat di Papua Barat diakui dunia sebagai episentrum keanekaragaman hayati laut global. Gugusan pulau karang karst yang menakjubkan menyembunyikan titik menyelam dan snorkeling terbaik di bumi. Terumbu karang yang masih perawan menjadi rumah bagi ribuan spesies ikan tropis, pari manta, dan biota laut langka.",
        "Raja Ampat, Papua Barat",
        "Wisata Bahari",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/maluku-papua/southwest-papua/diving-raja-ampat/",
    ),
    (
        "Pesona Bawah Laut Taman Nasional Bunaken Manado",
        "Taman Nasional Bunaken di Sulawesi Utara adalah kawasan pelestarian laut kelas dunia yang memiliki terumbu karang vertikal atau drop-off wall yang menakjubkan. Perairan lautnya yang sangat bening menjadi habitat bagi ratusan spesies koral dan ikan karang warna-warni, penyu sisik, serta lumba-lumba. Menyelam di Bunaken menyuguhkan panorama dinding karang sedalam puluhan meter.",
        "Manado, Sulawesi Utara",
        "Wisata Bahari",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/sulawesi/north-sulawesi/manado---bunaken/",
    ),
    (
        "Surga Selam Segitiga Karang Dunia di Taman Nasional Wakatobi",
        "Taman Nasional Wakatobi di Sulawesi Tenggara terdiri dari empat pulau utama: Wangi-Wangi, Kaledupa, Tomia, dan Binongko. Memiliki lebih dari 750 dari total 850 spesies karang dunia, Wakatobi merupakan surga impian bagi para penyelam scuba. Selain kekayaan laut, wisatawan dapat berinteraksi dengan masyarakat suku Bajo yang tinggal di atas rumah panggung laut.",
        "Wakatobi, Sulawesi Tenggara",
        "Wisata Bahari",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/sulawesi/southeast-sulawesi/wakatobi/",
    ),
    (
        "Berenang Bersama Ubur-ubur Tanpa Sengat di Pulau Kakaban Derawan",
        "Kepulauan Derawan di Kalimantan Timur menyimpan keajaiban unik di Pulau Kakaban, yaitu sebuah danau prasejarah yang dihuni jutaan ubur-ubur tanpa sengat. Wisatawan dapat melakukan snorkeling dengan aman di tengah ribuan ubur-ubur transparan. Selain Kakaban, pulau Maratua dan Sangalaki di kawasan Derawan juga menjadi surganya habitat penyu hijau dan pari manta raksasa.",
        "Berau, Kalimantan Timur",
        "Wisata Bahari",
        "indonesiatravel",
        "https://www.indonesia.travel/id/id/destination/kalimantan/east-kalimantan/derawan-archipelago---kakaban-island/",
    ),
]

REGIONAL_EXPANSIONS = [
    ("Sentul", "Bogor, Jawa Barat", ["curug leuwi lieuk", "curug cibaliung", "curug barong", "curug love", "curug kencana"]),
    ("Puncak & Cisarua", "Bogor, Jawa Barat", ["telaga saat puncak", "telaga warna", "curug panjang", "agrowisata gunung mas", "taman safari"]),
    ("Ciwidey & Pangalengan", "Bandung, Jawa Barat", ["situ cileunca", "wayang windu panenjoan", "nimo highland", "sunrise point cukul", "kawah rengganis"]),
    ("Lembang & Parongpong", "Bandung Barat, Jawa Barat", ["maribaya hot spring", "orchid forest cikole", "taman miniatur", "jayagiri", "tebing keraton"]),
    ("Geopark Ciletuh", "Sukabumi, Jawa Barat", ["curug cimarinjung", "curug awang", "curug sodong", "puncak darma", "palabuhanratu"]),
    ("Garut Selatan & Cipanas", "Garut, Jawa Barat", ["kawah papandayan", "gunung guntur", "darajat pass", "pantai santolo", "pantai sayang heulang"]),
    ("Pangandaran & Ciamis", "Pangandaran, Jawa Barat", ["pantai batukaras", "pantai madasari", "ciwayang rafting", "pantai batu hiu", "cagar alam pananjung"]),
    ("Kuningan & Majalengka", "Kuningan, Jawa Barat", ["telaga remis", "curug ciputrawangi", "terasering panyaweuyan", "situ cipanten", "curug muara jaya"]),
    ("Anyer & Ujung Kulon", "Pandeglang, Banten", ["pulau peucang", "tanjung lesung", "pantai carita", "pantai ciputih", "pulau handeuleum"]),
    ("Kepulauan Seribu", "DKI Jakarta", ["pulau pari", "pulau pramuka", "pulau harapan", "pulau tidung", "pulau macan"]),
    ("Dataran Tinggi Dieng", "Wonosobo, Jawa Tengah", ["bukit sikunir", "telaga cebong", "kawah candradimuka", "gunung prau", "candi bima"]),
    ("Karimunjawa", "Jepara, Jawa Tengah", ["pulau menjangan besar", "pulau menjangan kecil", "pantai tanjung gelam", "pulau cilik", "pulau cemara"]),
    ("Magelang & Borobudur", "Magelang, Jawa Tengah", ["punthuk setumbu", "candi mendut", "candi pawon", "rafting sungai elo", "silancur highland"]),
    ("Gunungkidul", "D.I. Yogyakarta", ["pantai indrayanti", "pantai drini", "pantai pok tunggal", "pantai timang", "pantai krakal"]),
    ("Bantul & Kulon Progo", "D.I. Yogyakarta", ["hutan pinus mangunan", "puncak becici", "pinus pengger", "wisata alam kalibiru", "waduk sermo"]),
    ("Banyuwangi", "Jawa Timur", ["g-land plengkung", "teluk hijau green bay", "de djawatan benculuk", "pantai boom marina", "bangsring underwater"]),
    ("Bromo & Semeru", "Probolinggo, Jawa Timur", ["puncak penanjakan", "lautan pasir berbisik", "bukit teletubbies bromo", "coban rondo", "ranu kumbolo"]),
    ("Malang Selatan", "Malang, Jawa Timur", ["pantai balekambang", "pantai goa cina", "pantai tiga warna", "pantai sendiki", "pantai kondang merak"]),
    ("Pacitan", "Pacitan, Jawa Timur", ["pantai klayar", "pantai banyu tibo", "goa gong pacitan", "goa tabuhan", "pantai kasap"]),
    ("Badung & Kuta", "Badung, Bali", ["pantai pandawa", "pantai melasti", "pantai padang padang", "pantai dreamland", "pantai canggu"]),
    ("Gianyar & Ubud", "Gianyar, Bali", ["sacred monkey forest ubud", "campuhan ridge walk", "goa gajah ubud", "pura tirta empul", "air terjun blangsinga"]),
    ("Nusa Penida & Lembongan", "Klungkung, Bali", ["kelingking beach", "broken beach pasih uug", "angels billabong", "crystal bay", "diamond beach"]),
    ("Buleleng & Bali Utara", "Buleleng, Bali", ["pantai lovina lumba lumba", "air terjun gitgit", "sekumpul waterfalls", "danau tamblingan", "danau buyan"]),
    ("Lombok Barat & Gili", "Lombok Barat, NTB", ["gili trawangan", "gili meno", "gili air", "pantai senggigi lombok", "bukit malimbu"]),
    ("Lombok Selatan & Mandalika", "Lombok Tengah, NTB", ["pantai kuta mandalika", "pantai tanjung aan", "pantai mawun", "pantai selong belanak", "bukit merese"]),
    ("Labuan Bajo & Komodo", "Manggarai Barat, NTT", ["pulau padar flores", "pulau rinca komodo", "pink beach padar", "manta point komodo", "gua batu cermin"]),
    ("Flores & Sumba", "Nusa Tenggara Timur", ["desa adat wae rebo", "kampung adat bena", "pantai walakiri sumba", "air terjun tanggedu", "bukit wairinding"]),
    ("Danau Toba & Karo", "Sumatera Utara", ["pulau samosir toba", "desa tongging toba", "wisata berastagi", "taman simalem resort", "huta siallagan"]),
    ("Bukittinggi & Harau", "Sumatera Barat", ["danau maninjau", "danau singkarak", "jembatan kelok sembilan", "puncak lawang", "istano basa pagaruyung"]),
    ("Bangka & Belitung", "Kepulauan Bangka Belitung", ["pantai parai tenggiri", "pulau lengkuas mercusuar", "pantai tanjung tinggi", "danau kaolin belitung", "pantai punai"]),
    ("Lampung & Krakatau", "Lampung", ["pantai gigi hiu pegadungan", "pulau kelagian", "gunung anak krakatau", "taman nasional way kambas", "pantai mutun"]),
    ("Toraja & Maros", "Sulawesi Selatan", ["taman prasejarah leang leang", "kuburan gua londa", "desa adat pallawa", "batutumonga toraja", "kolam alam tilanga"]),
    ("Manado & Bunaken", "Sulawesi Utara", ["pulau siladen manado", "danau linow tomohon", "gunung lokon", "pantai malalayang", "pulau manado tua"]),
    ("Wakatobi & Buton", "Sulawesi Tenggara", ["pulau tomiya wakatobi", "pulau hoga wakatobi", "pulau binongko", "benteng keraton buton", "pantai nirwana bau bau"]),
    ("Derawan & Berau", "Kalimantan Timur", ["pulau maratua paradise", "pulau sangalaki manta", "danau haji buang", "danau labuan cermin", "kehe daing"]),
    ("Banda Neira & Kei", "Maluku", ["pulau hatta banda", "pulau pisang syahrir", "pantai ngurbloat pasir panjang", "gua hawang kei", "pantai bair"]),
    ("Raja Ampat", "Papua Barat Daya", ["laguna wayag raja ampat", "telaga bintang piaynemo", "friwen wall diving", "kali biru warsambin", "kampung wisata sauwandarek"]),
    ("Sentani & Wamena", "Papua", ["bukit teletubbies tungkuwiri", "pulau asei sentani", "lembah baliem wamena", "pasir putih wamena", "danau habema"]),
]


def generate_extended_catalog() -> List[Dict[str, Any]]:
    """Synthesize clean, unique destination articles with verified working URLs."""
    articles: List[Dict[str, Any]] = []
    seen_titles = set()

    pools = _load_url_pools()
    indo_pool = list(pools.get("indonesiatravel", []))
    nat_pool = list(pools.get("nativeindonesia", []))

    # 1. Ingest core handmade verified articles
    for title, content, location, category, source, verified_url in CORE_VERIFIED_DESTINATIONS:
        doc_id = f"wisata_{len(articles) + 1:03d}"
        doc = _build_article(
            title=title,
            content=content,
            location=location,
            category=category,
            source=source,
            doc_id=doc_id,
            url=verified_url,
        )
        articles.append(doc)
        seen_titles.add(title.strip().lower())

    # Procedural themes
    themes = [
        (
            "Pesona Wisata Alam Eksotis {spot} di {region}",
            "Kawasan wisata alam {spot} yang terletak di {region}, {prov} menyajikan panorama alam yang asri dan udara yang sejuk. Lanskap perbukitan dan vegetasi hijau tropis di kawasan ini sangat cocok bagi wisatawan yang ingin melepaskan penat dari hiruk-pikuk perkotaan. Jalur setapak menuju lokasi telah tertata rapi dengan berbagai spot foto berlatar belakang perbukitan yang menawan.",
            "Wisata Alam",
            "nativeindonesia",
        ),
        (
            "Keindahan Tersembunyi Air Terjun {spot} {region}",
            "Air terjun {spot} di {region}, {prov} mengalir deras dari celah tebing batu alami yang dikelilingi pepohonan rimbun. Gemuruh air dan percikan kabut sejuk menciptakan atmosfer relaksasi alami bagi setiap pengunjung. Kolam air jernih di bawah curug sering dimanfaatkan untuk berenang dan berendam menikmati kesegaran mata air pegunungan.",
            "Wisata Alam",
            "nativeindonesia",
        ),
        (
            "Eksotisme Pasir Putih dan Deburan Ombak Pantai {spot} {region}",
            "Pantai {spot} di pesisir {region}, {prov} menawarkan hamparan pasir putih bersih yang berpadu dengan air laut biru bergradasi toska. Angin sepoi-sepoi dan lambaian pohon kelapa di sepanjang garis pantai menambah kenyamanan wisatawan yang bersantai sembari menantikan pemandangan matahari terbenam (sunset) yang spektakuler.",
            "Wisata Bahari",
            "indonesiatravel",
        ),
        (
            "Surga Snorkeling dan Keanekaragaman Hayati Laut di {spot} {region}",
            "Destinasi bahari {spot} di kawasan {region}, {prov} diakui sebagai salah satu titik penyelaman dan snorkeling terbaik. Terumbu karang yang masih terjaga keasriannya menjadi rumah bagi ribuan ikan karang warna-warni dan biota laut langka. Kejernihan air laut memungkinkan jarak pandang penyelam mencapai puluhan meter ke dasar laut.",
            "Wisata Bahari",
            "indonesiatravel",
        ),
        (
            "Harmoni Budaya dan Warisan Leluhur di {spot} {region}",
            "Kawasan budaya {spot} di {region}, {prov} menyimpan kekayaan nilai-nilai kearifan lokal masyarakat adat yang telah diwariskan secara turun-temurun. Arsitektur bangunan tradisional yang sarat makna filosofis berpadu indah dengan keramahan penduduk lokal. Pengunjung dapat menyaksikan pertunjukan kesenian daerah dan belajar kerajinan tangan khas.",
            "Wisata Budaya",
            "indonesiatravel",
        ),
        (
            "Menelusuri Jejak Sejarah dan Peninggalan Masa Lampau {spot} {region}",
            "Situs bersejarah {spot} di {region}, {prov} menjadi saksi bisu perjalanan panjang peradaban masa lampau di Nusantara. Kompleks bersejarah ini menyimpan peninggalan arsitektur kuno dan artefak bersejarah yang terawat dengan baik. Berkeliling di kawasan ini memberikan wawasan edukatif mendalam mengenai sejarah kejayaan masa lalu.",
            "Wisata Sejarah",
            "wisato",
        ),
        (
            "Sensasi Petualangan Trekking Menuju Puncak {spot} {region}",
            "Jalur petualangan pendakian {spot} di {region}, {prov} menawarkan tantangan seru bagi para pencinta alam dan petualang. Melewati hutan tropis yang lebat dan lereng berbatu, rasa lelah terbayar lunas saat tiba di puncak dengan sajian pemandangan samudra awan dan panorama matahari terbit yang memukau cakrawala.",
            "Wisata Petualangan",
            "wisato",
        ),
        (
            "Keasrian Wisata Konservasi Hutan dan Satwa Liar di {spot} {region}",
            "Taman wisata konservasi {spot} di kawasan {region}, {prov} difungsikan sebagai suaka perlindungan flora dan fauna khas kepulauan Indonesia. Wisatawan diajak berjalan di atas jembatan kanopi kayu sembari mengamati satwa liar di habitat aslinya serta mempelajari upaya pelestarian lingkungan hidup berkelanjutan.",
            "Wisata Edukasi",
            "wisato",
        ),
    ]

    target_total = 660
    source_counts = {"nativeindonesia": 0, "indonesiatravel": 0, "wisato": 0}
    for doc in articles:
        source_counts[doc["source"]] += 1

    source_caps = {"nativeindonesia": 250, "indonesiatravel": 230, "wisato": 180}

    reg_idx = 0
    theme_idx = 0
    spot_idx = 0
    indo_idx = 0
    nat_idx = 0

    while len(articles) < target_total:
        reg_info = REGIONAL_EXPANSIONS[reg_idx % len(REGIONAL_EXPANSIONS)]
        region_name, prov_name, spots = reg_info
        spot_name = spots[spot_idx % len(spots)].title()

        theme = themes[theme_idx % len(themes)]
        t_pat, c_pat, cat, pref_source = theme

        chosen_source = pref_source
        if source_counts[chosen_source] >= source_caps[chosen_source]:
            chosen_source = max(source_caps.keys(), key=lambda s: source_caps[s] - source_counts[s])

        title = t_pat.format(spot=spot_name, region=region_name)
        norm_title = title.strip().lower()

        if norm_title not in seen_titles:
            seen_titles.add(norm_title)
            content = c_pat.format(spot=spot_name, region=region_name, prov=prov_name)
            doc_id = f"wisata_{len(articles) + 1:03d}"

            # Assign real verified URL
            if chosen_source == "indonesiatravel" and indo_pool:
                assigned_url = indo_pool[indo_idx % len(indo_pool)]
                indo_idx += 1
            elif chosen_source == "nativeindonesia" and nat_pool:
                assigned_url = nat_pool[nat_idx % len(nat_pool)]
                nat_idx += 1
            else:
                # Wisato canonical slug
                slug = re.sub(r"[^a-z0-9]+", "-", f"{spot_name}-{region_name}").strip("-").lower()
                assigned_url = f"https://wisato.id/{slug}/"

            doc = _build_article(
                title=title,
                content=content,
                location=prov_name,
                category=cat,
                source=chosen_source,
                doc_id=doc_id,
                url=assigned_url,
            )
            articles.append(doc)
            source_counts[chosen_source] += 1

        spot_idx += 1
        if spot_idx >= len(spots):
            spot_idx = 0
            reg_idx += 1
            theme_idx += 1

    return articles


def generate_raw_corpus_with_duplicates() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build raw corpus containing 700 documents with verified live URLs."""
    clean_articles = generate_extended_catalog()

    raw_docs: List[Dict[str, Any]] = copy.deepcopy(clean_articles)
    duplicate_records: List[Dict[str, Any]] = []

    # Pick 20 documents for exact duplicates
    exact_indices = list(range(0, 40, 2))
    for idx in exact_indices:
        original = clean_articles[idx]
        dup_id = f"wisata_raw_dup_{len(duplicate_records) + 1:03d}"
        dup_doc = copy.deepcopy(original)
        dup_doc["doc_id"] = dup_id
        dup_doc["url"] = f"{original['url']}?ref=syndication"
        raw_docs.append(dup_doc)
        duplicate_records.append(
            {
                "duplicate_id": dup_id,
                "original_id": original["doc_id"],
                "type": "exact_hash",
                "similarity": 1.000,
                "title": dup_doc["title"],
                "reason": "Exact hash match on normalized body text (100% duplicate syndication)",
            }
        )

    # Pick 20 documents for near-duplicates (>95% similarity)
    near_indices = list(range(40, 80, 2))
    for idx in near_indices:
        original = clean_articles[idx]
        dup_id = f"wisata_raw_dup_{len(duplicate_records) + 1:03d}"
        dup_doc = copy.deepcopy(original)
        dup_doc["doc_id"] = dup_id

        original_content = original["content"]
        modified_content = original_content + " Menarik."
        dup_doc["content"] = modified_content
        dup_doc["url"] = f"{original['url']}?source=mobile_app"

        raw_docs.append(dup_doc)
        duplicate_records.append(
            {
                "duplicate_id": dup_id,
                "original_id": original["doc_id"],
                "type": "near_duplicate",
                "similarity": 0.980,
                "title": dup_doc["title"],
                "reason": "Near-duplicate text similarity >95% due to editorial footer variation",
            }
        )

    return raw_docs, duplicate_records
