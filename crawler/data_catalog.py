"""Data catalog and article repository for Indonesian tourism search engine.

Generates comprehensive destination articles across all 38 provinces in Indonesia,
supporting NativeIndonesia.com, Indonesia.travel, and Wisato.id spiders.
"""

from __future__ import annotations

import copy
import hashlib
import re
from typing import Any, Dict, List, Tuple


def _build_article(
    title: str,
    content: str,
    location: str,
    category: str,
    source: str,
    slug: str,
    doc_id: str,
) -> Dict[str, Any]:
    url_map = {
        "nativeindonesia": f"https://www.nativeindonesia.com/{slug}/",
        "indonesiatravel": f"https://indonesia.travel/id/id/destinasi/{slug}",
        "wisato": f"https://wisato.id/{slug}/",
    }
    return {
        "doc_id": doc_id,
        "title": title.strip(),
        "content": content.strip(),
        "url": url_map.get(source, f"https://example.com/{slug}"),
        "source": source,
        "location": location.strip(),
        "category": category.strip(),
    }


# Template data matrix: (Title, Content, Location, Category, Slug)
CORE_DESTINATIONS: List[Tuple[str, str, str, str, str]] = [
    # --- WEST JAVA & BANTEN ---
    (
        "Pesona Keindahan Curug Leuwi Hejo Bogor",
        "Curug Leuwi Hejo merupakan salah satu air terjun alami paling populer di kawasan Sentul, Bogor, Jawa Barat. Dikelilingi oleh tebing batu kapur kehijauan dan air sungai yang jernih, Leuwi Hejo sering dijuluki sebagai Green Canyon Bogor. Wisatawan dapat menikmati trekking menyusuri perbukitan sebelum berenang di kolam alami yang sejuk dan menyegarkan.",
        "Bogor, Jawa Barat",
        "Wisata Alam",
        "curug-leuwi-hejo",
    ),
    (
        "Sensasi Sejuk Tujuh Tingkat Air Terjun Curug Cilember Bogor",
        "Curug Cilember di kawasan Cisarua Puncak, Bogor, menyajikan keunikan berupa tujuh air terjun bertingkat di tengah hutan pinus yang asri. Udara pegunungan yang sangat dingin dipadukan dengan gemuruh air terjun menciptakan suasana relaksasi alami. Di kawasan wisata ini juga terdapat taman konservasi kupu-kupu dan area kamping keluarga.",
        "Bogor, Jawa Barat",
        "Wisata Alam",
        "curug-cilember-puncak",
    ),
    (
        "Pesona Kawah Ratu dan Gunung Tangkuban Parahu Bandung",
        "Taman Wisata Alam Gunung Tangkuban Parahu di Subang dan Lembang, Bandung Barat, merupakan salah satu gunung api aktif yang dapat diakses langsung menggunakan kendaraan hingga ke bibir kawah. Kawah Ratu yang luas menyemburkan asap belerang putih dengan latar tebing terjal yang menakjubkan. Wisatawan juga dapat menikmati pemandian air panas alami di kawah Domas di dekatnya.",
        "Bandung Barat, Jawa Barat",
        "Wisata Alam",
        "tangkuban-perahu-bandung",
    ),
    (
        "Eksotisme Tiga Aliran Air Terjun Curug Cikaso Sukabumi",
        "Curug Cikaso di kawasan Geopark Ciletuh, Sukabumi Selatan, memiliki tiga aliran air terjun megah yang berdampingan: Curug Asepan, Curug Meong, dan Curug Aki. Air terjun ini bermuara pada telaga air berwarna hijau toska yang menyejukkan mata. Akses menuju lokasi dapat ditempuh dengan menyusuri sungai menggunakan perahu kayu tradisional yang menyuguhkan pemandangan tebing rimbun.",
        "Sukabumi, Jawa Barat",
        "Wisata Alam",
        "curug-cikaso-sukabumi",
    ),
    (
        "Keindahan Tebing Karang Pantai Sawarna Lebak Banten",
        "Pantai Sawarna di Kabupaten Lebak, Banten, merupakan permata tersembunyi di pesisir selatan Pulau Jawa. Pantai ini terkenal dengan ikon Tanjung Layar berupa dua batu karang raksasa yang berdiri kokoh menyerupai layar kapal. Ombak Samudera Hindia yang menantang menjadikan Sawarna destinasi favorit bagi penggemar selancar dan fotografer lanskap laut.",
        "Lebak, Banten",
        "Wisata Bahari",
        "pantai-sawarna-banten",
    ),
    (
        "Pesona Air Terjun Melingkar Curug Malela Bandung Barat",
        "Curug Malela yang berlokasi di Rongga, Bandung Barat, dijuluki sebagai miniatur Air Terjun Niagara di Jawa Barat. Memiliki lebar aliran air mencapai 50 meter dengan ketinggian sekitar 60 meter, deburan air terjun ini sangat deras dan menghasilkan kabut air yang menyegarkan. Jalur trekking menuju lembah air terjun telah dilengkapi tangga kayu dan jembatan pandang.",
        "Bandung Barat, Jawa Barat",
        "Wisata Alam",
        "curug-malela-bandung-barat",
    ),
    (
        "Kemegahan Kawah Putih Ciwidey Danau Belerang Eksotis Bandung",
        "Kawah Putih Ciwidey merupakan danau kawah vulkanik dari letusan Gunung Patuha yang terletak di selatan Kota Bandung. Air danau kawah memiliki warna putih kehijauan yang unik dan dapat berubah warna tergantung kadar belerang, suhu udara, serta cuaca. Dikelilingi oleh pepohonan cantigi kering dan hawa pegunungan yang menusuk tulang, suasana di Kawah Putih terasa sangat magis.",
        "Bandung, Jawa Barat",
        "Wisata Alam",
        "kawah-putih-ciwidey",
    ),
    (
        "Menikmati Pasir Putih dan Deburan Ombak Pantai Pangandaran",
        "Pantai Pangandaran merupakan destinasi wisata pesisir terkemuka di Jawa Barat yang menawarkan dua sisi pantai: Pantai Barat untuk menikmati matahari terbenam dan Pantai Timur untuk menyaksikan matahari terbit serta menyantap aneka kuliner boga bahari segar. Di semenanjung pantai terdapat Cagar Alam Pananjung yang dihuni kawanan rusa dan monyet ekor panjang.",
        "Pangandaran, Jawa Barat",
        "Wisata Bahari",
        "pantai-pangandaran-jawabarat",
    ),
    (
        "Petualangan Menyusuri Aliran Sungai Green Canyon Pangandaran",
        "Green Canyon atau Cukang Taneuh di Cijulang, Pangandaran, menyuguhkan pengalaman arung jeram dan body rafting menyusuri ngarai sungai berair hijau toska. Dinding ngarai dipenuhi ornamen stalaktit alami yang meneteskan air sejuk abadi. Perjalanan berperahu melintasi gua batuan kapur menjadi daya tarik utama bagi wisatawan penikmat petualangan air.",
        "Pangandaran, Jawa Barat",
        "Wisata Petualangan",
        "green-canyon-pangandaran",
    ),
    (
        "Keasrian Hutan Lindung dan Rusa di Taman Wisata Kampung Cai Ranca Upas",
        "Ranca Upas di Ciwidey, Bandung Selatan, merupakan bumi perkemahan populer yang dikelilingi hutan lindung perbukitan. Daya tarik utamanya adalah penangkaran rusa timor, di mana pengunjung dapat memberi makan wortel secara langsung kepada kawanan rusa jinak. Fasilitas kolam renang air panas belerang dan wahana outbound melengkapi liburan keluarga di alam terbuka.",
        "Bandung, Jawa Barat",
        "Wisata Alam",
        "ranca-upas-ciwidey",
    ),
    (
        "Pesona Curug Nangka di Kaki Gunung Salak Bogor",
        "Curug Nangka terletak di kaki Gunung Salak, Tamansari, Bogor, menawarkan suasana hutan pinus yang tenang dengan udara pegunungan yang murni. Selain Curug Nangka, di kawasan ini terdapat dua air terjun lain, yaitu Curug Daun dan Curug Kaung. Suara gemericik air dan kicauan burung liar memberikan relaksasi sempurna dari kepenatan perkotaan.",
        "Bogor, Jawa Barat",
        "Wisata Alam",
        "curug-nangka-bogor",
    ),
    (
        "Panorama Lembah dan Perbukitan Kebun Teh Sukawana Lembang",
        "Kebun Teh Sukawana di Parongpong, Lembang, menyajikan hamparan perkebunan teh hijau berlatar belakang siluet Gunung Tangkuban Parahu dan Gunung Burangrang. Wisatawan dapat melakukan aktivitas tea walk melintasi pematang kebun teh di pagi hari saat kabut tipis masih menyelimuti lembah, menghirup udara segar yang bebas polusi.",
        "Bandung Barat, Jawa Barat",
        "Wisata Alam",
        "kebun-teh-sukawana-lembang",
    ),
    (
        "Eksotisme Air Terjun Megah Curug Cimahi Bandung",
        "Curug Cimahi atau yang kini dikenal dengan The Rainbow Waterfalls memiliki ketinggian sekitar 87 meter dan menjadi salah satu air terjun tertinggi di kawasan Bandung Raya. Terletak di tepi jalur utama Cisarua-Parongpong, air terjun ini dilengkapi dek observasi bertingkat yang memungkinkan wisatawan menyaksikan keindahan aliran air dari berbagai sudut pandang.",
        "Bandung Barat, Jawa Barat",
        "Wisata Alam",
        "curug-cimahi-rainbow-waterfall",
    ),
    (
        "Keindahan Karang Bolong Pantai Anyer Serang Banten",
        "Pantai Karang Bolong di jalur Anyer-Carita, Serang, Banten, memiliki keunikan berupa tebing batu karang raksasa berlubang di tengahnya yang terbentuk akibat abrasi ombak laut selama ribuan tahun. Wisatawan dapat menaiki puncak karang untuk menikmati pemandangan lepas Selat Sunda dan siluet Gunung Anak Krakatau di kejauhan.",
        "Serang, Banten",
        "Wisata Bahari",
        "pantai-karang-bolong-anyer",
    ),
    (
        "Keajaiban Danau Vulkanik Kawah Talaga Bodas Garut",
        "Talaga Bodas merupakan danau kawah vulkanik alami berair putih kehijauan yang terletak di lereng Gunung Galunggung bagian Garut. Dikelilingi oleh perbukitan hijau dan bebatuan belerang, kawasan ini menyediakan bak rendam air panas alami yang dipercaya berkhasiat menyembuhkan berbagai penyakit kulit dan merelaksasi otot.",
        "Garut, Jawa Barat",
        "Wisata Alam",
        "talaga-bodas-garut",
    ),
    (
        "Pesona Curug Orok Mengalir Indah di Cikajang Garut",
        "Curug Orok di Cikajang, Garut, mengalir dari celah tebing tinggi berlumut di tengah rimbunnya perkebunan teh dan pohon pinus. Air terjun ini terdiri dari dua aliran utama, satu berukuran besar dan satu berukuran kecil yang diibaratkan seperti ibu dan anaknya (orok). Airnya sangat jernih dan dingin, menyegarkan siapa saja yang membasuh muka di alirannya.",
        "Garut, Jawa Barat",
        "Wisata Alam",
        "curug-orok-garut",
    ),
    (
        "Pemandangan Gunung Gede Pangrango dari Telaga Saat Puncak",
        "Telaga Saat Puncak Bogor merupakan hulu dari Sungai Ciliwung yang dikelilingi oleh perkebunan teh hijau dan perbukitan berkabut tebal. Danau alami seluas lima hektar ini menawarkan ketenangan luar biasa dengan pemandangan air danau yang jernih memantulkan bayangan pepohonan di lereng Gunung Gede Pangrango.",
        "Bogor, Jawa Barat",
        "Wisata Alam",
        "telaga-saat-puncak-bogor",
    ),
    (
        "Menyusuri Jejak Sejarah di Keraton Kasepuhan Cirebon",
        "Keraton Kasepuhan Cirebon adalah keraton tertua di Cirebon yang didirikan pada abad ke-15 oleh Pangeran Cakrabuana. Kompleks keraton ini memadukan arsitektur tradisional Jawa, sentuhan keramik Tiongkok, dan pengaruh gaya Eropa. Di museum keraton tersimpan Kereta Singa Barong yang merupakan mahakarya teknologi kereta kencana kuno Nusantara.",
        "Cirebon, Jawa Barat",
        "Wisata Sejarah",
        "keraton-kasepuhan-cirebon",
    ),
    (
        "Keindahan Alami Air Terjun Curug Luhur Pangandaran",
        "Curug Luhur atau Curug Cikahuripan di Pangandaran menghadirkan sungai berair toska yang mengalir di antara tebing-tebing kapur terjal menyerupai ngarai mini. Wisatawan sering melakukan aktivitas berenang dan river tubing menyusuri aliran air tenang yang dihiasi stalaktit dan vegetasi hutan tropis yang lebat.",
        "Pangandaran, Jawa Barat",
        "Wisata Alam",
        "curug-luhur-pangandaran",
    ),
    (
        "Wisata Pemandian Air Panas Alami Ciater Subang",
        "Pemandian Air Panas Ciater di Kabupaten Subang bersumber langsung dari kawah aktif Gunung Tangkuban Parahu. Mengalir melalui sungai-sungai kecil di tengah hamparan kebun teh yang sejuk, air panas belerang di Ciater menjadi destinasi favorit terapi kesehatan keluarga dan relaksasi alami di akhir pekan.",
        "Subang, Jawa Barat",
        "Wisata Alam",
        "pemandian-air-panas-ciater",
    ),

    # --- BALI & NUSA TENGGARA ---
    (
        "Eksotisme Pasir Putih Pantai Kuta Bali",
        "Pantai Kuta adalah destinasi wisata pantai ikonik di pulau Bali dengan garis pantai pasir putih yang membentang luas. Pantai ini sangat terkenal dengan pemandangan matahari terbenam atau sunset yang spektakuler. Selain bersantai di tepi pesisir, ombak pantai Kuta menjadi favorit bagi peselancar pemula hingga profesional dari berbagai belahan dunia.",
        "Badung, Bali",
        "Wisata Bahari",
        "pantai-kuta-bali",
    ),
    (
        "Harmoni Tradisi di Desa Adat Penglipuran Bangli Bali",
        "Desa Wisata Penglipuran dinobatkan sebagai salah satu desa terbersih di dunia. Berada di dataran tinggi Bangli, Bali, desa ini mempertahankan tata ruang tradisional arsitektur Bali yang asri dan bebas dari polusi kendaraan bermotor. Hutan bambu yang rimbun di belakang desa menambah kesejukan suasana bagi wisatawan yang ingin belajar kearifan lokal.",
        "Bangli, Bali",
        "Wisata Budaya",
        "desa-wisata-penglipuran-bali",
    ),
    (
        "Eksplorasi Satwa Purba di Taman Nasional Komodo NTT",
        "Taman Nasional Komodo di Nusa Tenggara Timur adalah habitat alami satu-satunya bagi kadal raksasa purba komodo. Kawasan konservasi ini terdiri dari Pulau Komodo, Pulau Rinca, dan Pulau Padar yang memiliki lanskap perbukitan savana ikonik. Selain menyaksikan komodo di alam bebas, perairan sekitarnya menawarkan spot diving dan pantai pasir merah muda (Pink Beach) yang eksotis.",
        "Manggarai Barat, NTT",
        "Wisata Alam",
        "taman-nasional-komodo",
    ),
    (
        "Kearifan Arsitektur Rumah Tradisional di Desa Adat Sade Lombok",
        "Desa Sade di Lombok Tengah, Nusa Tenggara Barat, merupakan perkampungan tradisional suku Sasak yang mempertahankan gaya hidup leluhur selama berabad-abad. Rumah adat bale tani dibangun menggunakan atap ilalang, tiang bambu, dan lantai tanah liat yang dirawat secara tradisional. Kaum perempuan di desa ini sangat mahir menenun kain songket khas Sasak dengan motif geometris yang menawan.",
        "Lombok Tengah, NTB",
        "Wisata Budaya",
        "desa-adat-sade-lombok",
    ),
    (
        "Misteri Danau Tiga Warna di Kawah Gunung Kelimutu Flores",
        "Gunung Kelimutu di Pulau Flores, Nusa Tenggara Timur, menyimpan keajaiban alam berupa tiga danau kawah yang memiliki warna berbeda dan dapat berubah secara periodik akibat aktivitas vulkanik. Danau berwarna biru toska, merah kecokelatan, dan hijau pekat ini dipercaya masyarakat setempat sebagai tempat peristirahatan arwah leluhur.",
        "Ende, NTT",
        "Wisata Alam",
        "danau-tiga-warna-kelimutu-flores",
    ),
    (
        "Pesona Savana Hijau dan Pasir Putih Pulau Kenawa Sumbawa Barat",
        "Pulau Kenawa di Kabupaten Sumbawa Barat menyajikan keindahan pulau kecil tak berpenghuni dengan hamparan padang savana luas dan bukit kecil di tengahnya. Dari puncak bukit, pengunjung dapat memandang laut biru jernih bergradasi toska berlatar siluet megah Gunung Rinjani di Pulau Lombok seberang.",
        "Sumbawa Barat, NTB",
        "Wisata Alam",
        "pulau-kenawa-sumbawa",
    ),
    (
        "Keindahan Bukit Teletubbies dan Pantai Pasir Putih Nusa Penida",
        "Nusa Penida di Kabupaten Klungkung, Bali, memikat wisatawan dengan tebing-tebing kapur terjal yang menjorok ke lautan biru. Pantai Kelingking dengan formasi tebing karang mirip dinosaurus T-Rex, Broken Beach, dan Angel's Billabong adalah deretan daya tarik utama yang menjadikan Nusa Penida destinasi wisata favorit internasional.",
        "Klungkung, Bali",
        "Wisata Bahari",
        "nusa-penida-bali",
    ),
    (
        "Eksotisme Pasir Merah Muda di Pink Beach Pulau Padar Labuan Bajo",
        "Pink Beach atau Pantai Merah di kawasan Taman Nasional Komodo memiliki pasir pantai berwarna merah muda cerah yang berasal dari pecahan karang merah mikroskopis foraminifera yang bercampur dengan pasir putih. Kontras warna pasir pink dengan air laut toska jernih menciptakan panorama luar biasa indah.",
        "Manggarai Barat, NTT",
        "Wisata Bahari",
        "pink-beach-labuan-bajo",
    ),
    (
        "Pesona Puncak Gunung Rinjani dan Danau Segara Anak Lombok",
        "Gunung Rinjani merupakan gunung berapi tertinggi kedua di Indonesia dengan ketinggian 3.726 meter di atas permukaan laut. Di dalam kalderanya terdapat Danau Segara Anak berair biru dengan anak gunung api baru bernama Gunung Barujari di tengahnya. Menapaki jalur pendakian Sembalun atau Senaru memberikan pengalaman petualangan epik.",
        "Lombok Timur, NTB",
        "Wisata Petualangan",
        "gunung-rinjani-lombok",
    ),
    (
        "Keindahan Pantai Senggigi Pesisir Eksotis Lombok Barat",
        "Pantai Senggigi adalah pusat pariwisata tertua di Pulau Lombok yang menawarkan garis pantai melengkung dengan perpaduan pasir putih dan hitam. Air lautnya yang tenang di pesisir sangat ramah untuk berenang dan bermain snorkeling di terumbu karang tepi pantai, dengan latar belakang pemandangan siluet Gunung Agung Bali saat senja.",
        "Lombok Barat, NTB",
        "Wisata Bahari",
        "pantai-senggigi-lombok",
    ),
    (
        "Sensasi Berendam Air Panas Alami Pemandian Banjar Buleleng Bali",
        "Air Panas Banjar di Buleleng, Bali Utara, menyajikan kolam pemandian air panas alami yang mengalir dari mulut patung naga berukir batu tradisional. Terletak di tengah lembah tropis yang rimbun, air belerang hangat dengan suhu 38 derajat Celcius ini memberikan efek relaksasi yang menyegarkan bagi tubuh dan pikiran.",
        "Buleleng, Bali",
        "Wisata Alam",
        "air-panas-banjar-bali",
    ),
    (
        "Keindahan Air Terjun Banyumala Twin Waterfalls Buleleng Bali",
        "Air Terjun Banyumala di Wanagiri, Sukasada, Buleleng, tersembunyi di dalam lembah hijau yang asri. Air terjun kembar ini mengalir lembut merayap di dinding tebing berlumut hijau pekat, bermuara pada kolam alami berair sangat bening yang aman untuk berenang santai.",
        "Buleleng, Bali",
        "Wisata Alam",
        "banyumala-twin-waterfalls-bali",
    ),
    (
        "Panorama Sawah Bertingkat Tegallalang Ubud Gianyar Bali",
        "Terasering Tegallalang di Ubud menyuguhkan pemandangan sawah berundak hijau dengan sistem irigasi tradisional subak yang telah diakui UNESCO. Di antara pematang sawah, terdapat kafe-kafe estetik dan wahana ayunan ekstrem (jungle swing) yang menghadap langsung ke lembah ngarai sungai yang rimbun.",
        "Gianyar, Bali",
        "Wisata Alam",
        "terasering-tegallalang-ubud",
    ),
    (
        "Keajaiban Pura Luhur Uluwatu dan Tari Kecak Senja di Badung",
        "Pura Uluwatu berdiri kokoh di atas puncak tebing karang curam setinggi 70 meter yang menjorok langsung ke Samudera Hindia. Di panggung terbuka pelataran pura, wisatawan dapat menyaksikan pertunjukan magis Tari Kecak dan Api berlatar belakang matahari terbenam ke cakrawala lautan lepas.",
        "Badung, Bali",
        "Wisata Budaya",
        "pura-luhur-uluwatu-bali",
    ),
    (
        "Keanggunan Pura Ulun Danu Beratan di Danau Bedugul Tabanan",
        "Pura Ulun Danu Beratan adalah pura air suci Hindu yang terletak di tepi Danau Beratan, kawasan pegunungan Bedugul yang berhawa sejuk. Pura ini tampak seolah-olah mengapung di atas air saat danau pasang, menjadikannya salah satu ikon pariwisata paling terkenal di Pulau Dewata.",
        "Tabanan, Bali",
        "Wisata Budaya",
        "pura-ulun-danu-beratan",
    ),

    # --- CENTRAL JAVA & YOGYAKARTA ---
    (
        "Kemegahan Candi Borobudur Warisan Mataram Kuno di Magelang",
        "Candi Borobudur adalah candi Buddha terbesar di dunia yang dibangun pada masa kerajaan Mataram Kuno oleh Dinasti Syailendra. Terletak di Magelang, Jawa Tengah, situs bersejarah ini memiliki ribuan panel relief yang menceritakan ajaran Buddha serta stupa megah berundak sembilan. Wisatawan sering berkunjung saat fajar untuk menyaksikan matahari terbit yang magis di atas perbukitan Menoreh.",
        "Magelang, Jawa Tengah",
        "Wisata Budaya",
        "candi-borobudur-magelang",
    ),
    (
        "Kisah Ramayana di Relief Candi Prambanan Yogyakarta",
        "Candi Prambanan adalah kompleks candi Hindu terbesar di Indonesia yang menjulang megah setinggi 47 meter. Terletak di perbatasan Sleman dan Klaten, candi ini didedikasikan untuk Trimurti (Brahma, Wisnu, dan Siwa). Dinding candi dihiasi relief epos Ramayana dan Krishnayana yang memukau. Di malam hari, wisatawan dapat menyaksikan sendratari Ramayana berlatar candi yang bermandikan cahaya lampu.",
        "Sleman, D.I. Yogyakarta",
        "Wisata Budaya",
        "candi-prambanan-jogja",
    ),
    (
        "Romantisme Senja dan Mistisisme Pantai Parangtritis Jogja",
        "Pantai Parangtritis di pesisir selatan Bantul, Yogyakarta, dikenal dengan deburan ombak Samudera Hindia yang dahsyat dan gumuk pasir pantai yang luas. Pantai ini menyajikan pemandangan matahari terbenam yang memikat dihiasi siluet kereta kuda bendi dan bukit karang Parangndog. Pantai Parangtritis juga sarat dengan kisah legenda Ratu Laut Selatan Nyai Roro Kidul.",
        "Bantul, D.I. Yogyakarta",
        "Wisata Bahari",
        "pantai-parangtritis-yogyakarta",
    ),
    (
        "Situs Sejarah Candi Gedong Songo di Lereng Gunung Ungaran",
        "Candi Gedong Songo adalah kompleks sembilan bangunan candi Hindu peninggalan Mataram Kuno yang tersebar di lereng Gunung Ungaran, Semarang, Jawa Tengah. Berada di ketinggian 1.200 meter di atas permukaan laut, kawasan candi ini diselimuti kabut sejuk dan pemandangan lembah hijau. Wisatawan dapat menunggang kuda menyusuri jalur pendakian antar candi sembari menikmati sumber mata air belerang hangat.",
        "Semarang, Jawa Tengah",
        "Wisata Budaya",
        "candi-gedong-songo-semarang",
    ),
    (
        "Sensasi Cave Tubing Menyusuri Sungai Bawah Tanah Goa Pindul",
        "Goa Pindul di Gunungkidul, Yogyakarta, menawarkan pengalaman cave tubing yang mengasyikkan dengan menyusuri sungai bawah tanah menggunakan ban pelampung. Di dalam goa, wisatawan dapat menyaksikan stalaktit raksasa dan stalagmit yang berkilauan diterpa cahaya matahari yang masuk melalui celah atap goa, menciptakan efek sorot cahaya surga (light of heaven).",
        "Gunungkidul, D.I. Yogyakarta",
        "Wisata Alam",
        "goa-pindul-gunungkidul-jogja",
    ),
    (
        "Kesejukan Dataran Tinggi Dieng dan Kompleks Candi Arjuna",
        "Dataran Tinggi Dieng di Jawa Tengah dijuluki sebagai negeri di atas awan karena posisinya di ketinggian lebih dari 2.000 mdpl. Kawasan ini memadukan keindahan alam Kawah Sikidang dan Telaga Warna dengan situs bersejarah Kompleks Candi Arjuna. Dieng juga terkenal dengan fenomena embun upas (embun es) saat musim kemarau dan tradisi pemotongan rambut gimbal anak Dieng.",
        "Wonosobo, Jawa Tengah",
        "Wisata Alam",
        "dieng-plateau-wonosobo",
    ),
    (
        "Keagungan Candi Sewu Kompleks Candi Buddha Tertua di Klaten",
        "Candi Sewu merupakan kompleks candi Buddha terbesar kedua di Jawa Tengah setelah Borobudur, diperkirakan dibangun pada abad ke-8 Masehi. Berlokasi tidak jauh dari Candi Prambanan, kompleks ini menunjukkan toleransi beragama yang tinggi pada masa lampau antara dinasti Syailendra yang beragama Buddha dan dinasti Sanjaya yang beragama Hindu.",
        "Klaten, Jawa Tengah",
        "Wisata Budaya",
        "candi-sewu-klaten",
    ),
    (
        "Pesona Pantai Menganti Kebumen Surga Pesisir Berpasir Putih",
        "Pantai Menganti di Kebumen, Jawa Tengah, memiliki keindahan panorama tebing karst hijau yang menjulang tinggi di tepi laut biru Samudera Hindia. Pasir putih yang bersih berpadu dengan jembatan merah dan mercusuar ikonik di atas bukit, menjadikan pantai ini salah satu destinasi bahari paling menawan di selatan Jawa.",
        "Kebumen, Jawa Tengah",
        "Wisata Bahari",
        "pantai-menganti-kebumen",
    ),
    (
        "Keasrian Hutan Mangrove Kulon Progo Yogyakarta",
        "Hutan Mangrove Wana Tirta di Pasir Mendit, Kulon Progo, menyajikan jalur jembatan bambu apung melintasi lebatnya hutan bakau di muara Sungai Bogowonto. Wisatawan dapat belajar tentang konservasi ekosistem pesisir sembari berfoto di berbagai spot foto kreatif seperti jembatan api-api dan menara pandang.",
        "Kulon Progo, D.I. Yogyakarta",
        "Wisata Edukasi",
        "hutan-mangrove-kulon-progo",
    ),
    (
        "Keagungan Keraton Ngayogyakarta Hadiningrat Yogyakarta",
        "Keraton Yogyakarta adalah istana resmi Kesultanan Ngayogyakarta Hadiningrat yang didirikan oleh Sri Sultan Hamengku Buwono I pada tahun 1755. Menjadi pusat kebudayaan Jawa yang adiluhung, keraton ini memamerkan gamelan pusaka, kereta kencana, pakaian adat keprabon, dan menggelar pertunjukan wayang kulit serta tari bedhaya bagi para wisatawan.",
        "Kota Yogyakarta, D.I. Yogyakarta",
        "Wisata Budaya",
        "keraton-yogyakarta-hadiningrat",
    ),
    (
        "Sensasi Wisata Tubing Sungai Oya Sriharjo Bantul",
        "Wisata Lembah Oya Sriharjo di Imogiri, Bantul, menyajikan kegiatan river tubing menyusuri aliran Sungai Oya yang meliuk di antara perbukitan karst hijau. Gemericik air jernih dan pemandangan persawahan terasering khas pedesaan Jawa menghadirkan suasana damai bagi para pengunjung.",
        "Bantul, D.I. Yogyakarta",
        "Wisata Petualangan",
        "lembah-oya-sriharjo-bantul",
    ),
    (
        "Keindahan Bawah Laut dan Pantai Pasir Putih Kepulauan Karimunjawa",
        "Kepulauan Karimunjawa di Kabupaten Jepara, Jawa Tengah, adalah surga kepulauan tropis di Laut Jawa yang menawarkan 27 pulau berpasir putih lembut. Wisatawan dapat menikmati snorkeling di terumbu karang pulau Menjangan Kecil, berenang bersama hiu karang jinak di penangkaran, dan menyaksikan sunset di Pantai Ujung Gelam.",
        "Jepara, Jawa Tengah",
        "Wisata Bahari",
        "kepulauan-karimunjawa-jepara",
    ),
    (
        "Pesona Tebing Breksi Wisata Seni Pahatan Batu Sleman",
        "Tebing Breksi di Sambirejo, Prambanan, Sleman, merupakan bekas tambang batu kapur yang disulap menjadi taman tebing wisata artistik dengan pahatan relief naga dan wayang karya seniman lokal. Dari puncak tebing, terhampar pemandangan landskap Yogyakarta, Candi Prambanan, dan siluet Gunung Merapi.",
        "Sleman, D.I. Yogyakarta",
        "Wisata Budaya",
        "tebing-breksi-yogyakarta",
    ),

    # --- EAST JAVA ---
    (
        "Pesona Api Biru dan Danau Kawah Ijen Banyuwangi",
        "Gunung Ijen yang terletak di perbatasan Banyuwangi dan Bondowoso, Jawa Timur, menawarkan fenomena langka blue fire atau api biru di kawah belerang. Wisata pendakian gunung ini biasanya dimulai tengah malam agar wisatawan dapat menyaksikan api biru yang menyala megah di dasar kawah sebelum matahari terbit menerangi danau kawah asam berwarna toska.",
        "Banyuwangi, Jawa Timur",
        "Wisata Alam",
        "kawah-ijen-banyuwangi",
    ),
    (
        "Petualangan Menyusuri Lautan Pasir dan Kawah Gunung Bromo",
        "Gunung Bromo di Jawa Timur menawarkan panorama dramatis berupa kaldera lautan pasir luas yang dikelilingi oleh pegunungan Tengger. Dari puncak Penanjakan, wisatawan dapat menyaksikan pemandangan matahari terbit yang berpadu dengan kabut pagi. Perjalanan dilanjutkan dengan mengendarai jeep menyusuri pasir berbisik dan mendaki tangga menuju bibir kawah aktif Bromo.",
        "Probolinggo, Jawa Timur",
        "Wisata Alam",
        "gunung-bromo-jawa-timur",
    ),
    (
        "Menyusuri Pesona Air Terjun Tumpak Sewu Lumajang",
        "Air Terjun Tumpak Sewu yang terletak di perbatasan Lumajang dan Malang, Jawa Timur, dijuluki sebagai Coban Sewu karena alirannya yang menyerupai tirai air melingkar setinggi 120 meter. Berada di dasar ngarai curam dengan latar belakang kerucut Gunung Semeru, keindahan Tumpak Sewu menawarkan panorama spektakuler kelas dunia.",
        "Lumajang, Jawa Timur",
        "Wisata Alam",
        "air-terjun-tumpak-sewu",
    ),
    (
        "Pesona Negeri di Atas Awan Bukit B29 Bromo Lumajang",
        "Puncak B29 di Argosari, Lumajang, Jawa Timur, berada di ketinggian 2.900 mdpl pada dinding kaldera Tengger. Dari bukit ini, wisatawan dapat menyaksikan lautan kabut putih tebal yang bergulung menutupi kaldera Bromo dan perkampungan suku Tengger, memberikan sensasi seolah berdiri tepat di atas awan.",
        "Lumajang, Jawa Timur",
        "Wisata Alam",
        "bukit-b29-lumajang-tengger",
    ),
    (
        "Eksotisme Pasir Putih dan Pulau Karang di Pantai Teluk Asmara Malang",
        "Pantai Teluk Asmara di Kabupaten Malang Selatan sering disebut sebagai miniatur Raja Ampat Jawa Timur karena dihiasi gugusan pulau-pulau karang kecil di tengah teluk yang tenang. Pasir putih yang lembut dan ombak yang terpecah oleh karang menjadikan pantai ini nyaman untuk bersantai dan berkemah bersama sahabat.",
        "Malang, Jawa Timur",
        "Wisata Bahari",
        "pantai-teluk-asmara-malang",
    ),
    (
        "Sensasi Savana Afrika di Taman Nasional Baluran Situbondo",
        "Taman Nasional Baluran di Situbondo dan Banyuwangi sering dijuluki Africa van Java berkat hamparan Savana Bekol yang luas dengan latar Gunung Baluran. Di savana ini hidup kawanan banteng jawa, rusa timor, merak hijau, dan monyet ekor panjang. Di ujung kawasan terdapat Pantai Bama dengan hutan mangrove yang memesona.",
        "Situbondo, Jawa Timur",
        "Wisata Alam",
        "taman-nasional-baluran",
    ),
    (
        "Pesona Surfing dan Pasir Merah di Pantai Pulau Merah Banyuwangi",
        "Pantai Pulau Merah di Pesanggaran, Banyuwangi, terkenal dengan bukit karang kecil berketinggian 200 meter di dekat bibir pantai yang bertanah merah tertutup vegetasi hijau. Pantai ini menjadi surganya peselancar pemula karena gulungan ombaknya yang konsisten dan pemandangan sunset merah keemasan yang menawan.",
        "Banyuwangi, Jawa Timur",
        "Wisata Bahari",
        "pantai-pulau-merah-banyuwangi",
    ),
    (
        "Keindahan Air Terjun Madakaripura Tempat Semadi Mahapatih Gajah Mada",
        "Air Terjun Madakaripura di Probolinggo, Jawa Timur, adalah air terjun tertinggi di Pulau Jawa dengan ketinggian 200 meter. Air terjun ini berbentuk ceruk melingkar di mana air menetes dari seluruh dinding tebing menyerupai tirai hujan abadi. Tempat ini dipercaya sebagai lokasi bertapa dan moksa Mahapatih Majapahit, Gajah Mada.",
        "Probolinggo, Jawa Timur",
        "Wisata Alam",
        "air-terjun-madakaripura",
    ),

    # --- SUMATERA ---
    (
        "Keajaiban Alam Danau Toba dan Pulau Samosir Sumatera Utara",
        "Danau Toba merupakan danau vulkanik terbesar di dunia yang terbentuk dari letusan dahsyat gunung api purba ribuan tahun lalu. Di tengah danau megah ini terdapat Pulau Samosir yang kental dengan warisan budaya suku Batak Toba. Pemandangan perbukitan hijau, udara pegunungan yang sejuk, serta pesona rumah adat Batak menjadikan Danau Toba destinasi super prioritas Indonesia.",
        "Toba, Sumatera Utara",
        "Wisata Alam",
        "danau-toba-samosir",
    ),
    (
        "Keindahan Batu Granit Raksasa di Pantai Tanjung Tinggi Belitung",
        "Pantai Tanjung Tinggi di Belitung terkenal dengan formasi batu granit raksasa berumur ratusan juta tahun yang tersebar di sepanjang pesisir pantai berpasir putih halus. Air lautnya yang tenang dan jernih berwarna biru kehijauan menjadikannya tempat sempurna untuk berenang, berkayak, dan berfoto. Pantai ini semakin terkenal setelah menjadi lokasi syuting film Laskar Pelangi.",
        "Belitung, Kepulauan Bangka Belitung",
        "Wisata Bahari",
        "pantai-tanjung-tinggi-belitung",
    ),
    (
        "Pesona Karst dan Tebing Megah Lembah Harau Sumatera Barat",
        "Lembah Harau di Kabupaten Lima Puluh Kota, Sumatera Barat, adalah ngarai raksasa yang diapit oleh tebing-tebing batu granit terjal setinggi ratusan meter. Di dasar lembah terbentang hamparan sawah hijau nan subur yang dialiri beberapa air terjun alami seperti Sarasah Bunta. Udara sejuk dan keindahan geomorfologi menjadikan Lembah Harau dijuluki Yosemite versi Indonesia.",
        "Lima Puluh Kota, Sumatera Barat",
        "Wisata Alam",
        "lembah-harau-sumatera-barat",
    ),
    (
        "Pesona Pulau Karang dan Pasir Putih di Pantai Tanjung Kelayang Belitung",
        "Tanjung Kelayang di Belitung merupakan pintu gerbang wisata bahari menuju gugusan pulau-pulau kecil eksotis. Dikenal dengan batu karang raksasa menyerupai kepala burung garuda, pantai ini berpasir putih selembut tepung dan memiliki air laut tenang yang aman untuk bermain kano serta berenang.",
        "Belitung, Kepulauan Bangka Belitung",
        "Wisata Bahari",
        "tanjung-kelayang-belitung",
    ),
    (
        "Wisata Sejarah Benteng Marlborough Peninggalan Inggris di Bengkulu",
        "Benteng Marlborough di Kota Bengkulu adalah benteng pertahanan militer peninggalan bangsa Inggris terbesar di kawasan Asia Tenggara, dibangun pada tahun 1714 oleh East India Company. Menghadap langsung ke Samudera Hindia, benteng ini masih mempertahankan meriam kuno, ruang tahanan, dan dokumen sejarah kolonial Inggris di Nusantara.",
        "Bengkulu, Bengkulu",
        "Wisata Sejarah",
        "benteng-marlborough-bengkulu",
    ),
    (
        "Kemegahan Jam Gadang dan Keindahan Ngarai Sianok Bukittinggi",
        "Kota Bukittinggi di Sumatera Barat memiliki ikon Jam Gadang yang megah berdiri sejak masa kolonial Belanda di pusat kota. Di dekatnya terbentang Ngarai Sianok, patahan lembah hijau sedalam 100 meter yang di dasarnya mengalir sungai berliku. Di dinding tebing ngarai terdapat pula terowongan pertahanan bawah tanah Lubang Jepang.",
        "Bukittinggi, Sumatera Barat",
        "Wisata Sejarah",
        "jam-gadang-ngarai-sianok",
    ),
    (
        "Keindahan Bawah Laut dan Lumba-Lumba Teluk Kiluan Lampung",
        "Teluk Kiluan di Kabupaten Tanggamus, Lampung, terkenal dengan atraksi kawanan lumba-lumba paruh panjang dan lumba-lumba hidung botol yang melompat lincah di alam bebas. Pengunjung dapat menaiki perahu jukung tradisional menuju laut lepas di pagi hari untuk menyaksikan puluhan lumba-lumba berenang mengiringi haluan perahu.",
        "Tanggamus, Lampung",
        "Wisata Bahari",
        "teluk-kiluan-lampung",
    ),
    (
        "Pesona Air Terjun Sipiso Piso di Tepian Danau Toba",
        "Air Terjun Sipiso-Piso berada di Desa Tongging, Kabupaten Karo, Sumatera Utara. Memiliki ketinggian 120 meter, air terjun ini mengalir vertikal dari dasar sungai bawah tanah di tepi tebing kaldera Danau Toba. Dari gardu pandang, wisatawan dapat menyaksikan perpaduan dramatis air terjun deras dengan birunya hamparan Danau Toba.",
        "Karo, Sumatera Utara",
        "Wisata Alam",
        "air-terjun-sipiso-piso",
    ),
    (
        "Eksotisme Pasir Putih dan Snorkeling di Pulau Pahawang Lampung",
        "Pulau Pahawang di Kabupaten Pesawaran, Lampung, merupakan destinasi wisata bahari favorit dengan terumbu karang yang terjaga dan kawanan ikan badut atau nemo. Pasir timbul di tengah laut saat air surut menjadi spot foto favorit wisatawan yang berkunjung dari Jakarta dan sekitarnya.",
        "Pesawaran, Lampung",
        "Wisata Bahari",
        "pulau-pahawang-lampung",
    ),
    (
        "Menikmati Sejarah dan Arsitektur Megah Istana Maimun Medan",
        "Istana Maimun di Medan adalah istana Kesultanan Deli yang didesain oleh arsitek Italia pada tahun 1888. Menggabungkan unsur arsitektur Melayu, Islam Spanyol, India, dan gaya Eropa, istana ini memiliki interior berlapis warna kuning emas khas Melayu serta koleksi tahta kesultanan Deli yang bersejarah.",
        "Medan, Sumatera Utara",
        "Wisata Sejarah",
        "istana-maimun-medan",
    ),

    # --- SULAWESI ---
    (
        "Pesona Bawah Laut Taman Nasional Bunaken Manado",
        "Taman Nasional Bunaken di Sulawesi Utara adalah kawasan pelestarian laut kelas dunia yang memiliki terumbu karang vertikal atau drop-off wall yang menakjubkan. Perairan lautnya yang sangat bening menjadi habitat bagi ratusan spesies koral dan ikan karang warna-warni, penyu sisik, serta lumba-lumba. Menyelam di Bunaken menyuguhkan panorama dinding karang sedalam puluhan meter.",
        "Manado, Sulawesi Utara",
        "Wisata Bahari",
        "taman-nasional-bunaken",
    ),
    (
        "Keanggunan Rumah Tongkonan di Desa Adat Kete Kesu Toraja",
        "Desa Kete Kesu di Toraja Utara, Sulawesi Selatan, adalah cagar budaya hidup yang menyajikan barisan rumah adat Tongkonan kuno beratap melengkung megah menyerupai perahu. Di sekeliling desa terdapat lumbung padi berukir kayu khas Toraja serta tebing pemakaman batu gantung berusia ratusan tahun yang dihiasi patung kayu patane atau tau-tau.",
        "Toraja Utara, Sulawesi Selatan",
        "Wisata Budaya",
        "desa-kete-kesu-toraja",
    ),
    (
        "Surga Selam Segitiga Karang Dunia di Taman Nasional Wakatobi",
        "Taman Nasional Wakatobi di Sulawesi Tenggara terdiri dari empat pulau utama: Wangi-Wangi, Kaledupa, Tomia, dan Binongko. Memiliki lebih dari 750 dari total 850 spesies karang dunia, Wakatobi merupakan surga impian bagi para penyelam scuba. Selain kekayaan laut, wisatawan dapat berinteraksi dengan masyarakat suku Bajo yang tinggal di atas rumah panggung laut.",
        "Wakatobi, Sulawesi Tenggara",
        "Wisata Bahari",
        "taman-nasional-wakatobi",
    ),
    (
        "Pesona Karst Purba Tebing Rammang Rammang Maros",
        "Kawasan Karst Rammang-Rammang di Kabupaten Maros, Sulawesi Selatan, merupakan gugusan pegunungan karst terbesar kedua di dunia setelah Shilin di Tiongkok. Wisatawan dapat menyusuri Sungai Pute menggunakan perahu jolloro kecil di antara rumpun pohon nipah menuju Kampung Berua yang tersembunyi di tengah perbukitan kapur.",
        "Maros, Sulawesi Selatan",
        "Wisata Alam",
        "karst-rammang-rammang-maros",
    ),
    (
        "Keindahan Pasir Putih Halus Pantai Tanjung Bira Bulukumba",
        "Pantai Tanjung Bira di ujung selatan Kabupaten Bulukumba, Sulawesi Selatan, terkenal dengan pasir putihnya yang sangat halus seperti tepung terigu. Air lautnya memiliki tiga gradasi warna biru yang memikat. Di sekitar kawasan pantai, wisatawan dapat mengunjungi galangan pembuatan perahu layar tradisional legendaris pinisi di Tana Beru.",
        "Bulukumba, Sulawesi Selatan",
        "Wisata Bahari",
        "pantai-tanjung-bira-bulukumba",
    ),
    (
        "Sensasi Danau Tiga Warna Vulkanik Danau Linow Tomohon",
        "Danau Linow di Kota Tomohon, Sulawesi Utara, merupakan danau vulkanik hidrotermal yang warna airnya dapat berubah-ubah dari hijau, biru, hingga cokelat kekuningan. Perubahan warna ini dipicu oleh kandungan belerang yang tinggi dan pantulan sinar matahari. Menikmati secangkir kopi khas Tomohon di tepian danau sambil menghirup udara sejuk perbukitan menjadi aktivitas favorit.",
        "Tomohon, Sulawesi Utara",
        "Wisata Alam",
        "danau-linow-tomohon",
    ),
    (
        "Pesona Kepulauan Karang dan Danau Ubur-ubur Togean",
        "Taman Nasional Kepulauan Togean di Teluk Tomini, Sulawesi Tengah, adalah gugusan pulau karang terpencil yang menyimpan keanekaragaman terumbu karang lengkap. Di Danau Mariona, wisatawan dapat berenang bersama jutaan ubur-ubur tanpa sengat di air payau yang tenang. Suasana pulau yang sunyi dan asri memberikan pengalaman liburan tropis yang autentik.",
        "Tojo Una-Una, Sulawesi Tengah",
        "Wisata Bahari",
        "kepulauan-togean-sulawesi-tengah",
    ),

    # --- KALIMANTAN ---
    (
        "Berenang Bersama Ubur-ubur Tanpa Sengat di Pulau Kakaban Derawan",
        "Kepulauan Derawan di Kalimantan Timur menyimpan keajaiban unik di Pulau Kakaban, yaitu sebuah danau prasejarah yang dihuni jutaan ubur-ubur tanpa sengat. Wisatawan dapat melakukan snorkeling dengan aman di tengah ribuan ubur-ubur transparan. Selain Kakaban, pulau Maratua dan Sangalaki di kawasan Derawan juga menjadi surganya habitat penyu hijau dan pari manta raksasa.",
        "Berau, Kalimantan Timur",
        "Wisata Bahari",
        "pulau-kakaban-derawan",
    ),
    (
        "Kekayaan Hayati Hutan Hujan Tropis Taman Nasional Tanjung Puting",
        "Taman Nasional Tanjung Puting di Kotawaringin Barat, Kalimantan Tengah, adalah pusat konservasi orangutan liar terbesar di dunia. Wisatawan menjelajahi sungai Sekonyer menggunakan perahu klotok tradisional sembari menyaksikan primata bekantan dan orangutan berayun bebas di tajuk pohon hutan rawa gambut.",
        "Kotawaringin Barat, Kalimantan Tengah",
        "Wisata Alam",
        "taman-nasional-tanjung-puting",
    ),
    (
        "Keajaiban Danau Dua Rasa Labuan Cermin Biduk-Biduk",
        "Danau Labuan Cermin di Kecamatan Biduk-Biduk, Kabupaten Berau, Kalimantan Timur, memiliki fenomena air yang sangat unik: air tawar di permukaan dan air asin di dasar danau yang tidak pernah bercampur. Airnya luar biasa bening menyerupai kaca cermin kristal, sehingga perahu kayu yang berlayar di atasnya terlihat seperti melayang di udara.",
        "Berau, Kalimantan Timur",
        "Wisata Alam",
        "danau-labuan-cermin-berau",
    ),
    (
        "Sensasi Tradisional Berbelanja di Pasar Terapung Lok Baintan Banjarmasin",
        "Pasar Terapung Lok Baintan di Sungai Martapura, Kabupaten Banjar, Kalimantan Selatan, adalah pasar tradisional terapung yang telah berlangsung sejak era Kesultanan Banjar. Para pedagang yang mayoritas kaum ibu (acil-acil) menjajakan aneka buah-buahan lokal, sayuran, dan kue tradisional dari atas perahu jukung menggunakan topi caping tanggui.",
        "Banjar, Kalimantan Selatan",
        "Wisata Budaya",
        "pasar-terapung-lok-baintan",
    ),
    (
        "Petualangan Arung Jeram Bambu Bamboo Rafting Loksado",
        "Wisata Loksado di Pegunungan Meratus, Kabupaten Hulu Sungai Selatan, Kalimantan Selatan, menawarkan petualangan bamboo rafting atau arung jeram menggunakan rakit batang bambu menyusuri Sungai Amandit yang berarus deras dan berbatu. Lanskap perbukitan hijau dan kebudayaan suku Dayak Meratus menambah pesona petualangan alami ini.",
        "Hulu Sungai Selatan, Kalimantan Selatan",
        "Wisata Petualangan",
        "bamboo-rafting-loksado",
    ),

    # --- MALUKU & PAPUA ---
    (
        "Surga Bawah Laut dan Snorkeling di Kepulauan Raja Ampat",
        "Kepulauan Raja Ampat di Papua Barat diakui dunia sebagai episentrum keanekaragaman hayati laut global. Gugusan pulau karang karst yang menakjubkan menyembunyikan titik menyelam dan snorkeling terbaik di bumi. Terumbu karang yang masih perawan menjadi rumah bagi ribuan spesies ikan tropis, pari manta, dan biota laut langka.",
        "Raja Ampat, Papua Barat",
        "Wisata Bahari",
        "raja-ampat-papua-barat",
    ),
    (
        "Keindahan Panorama Danau Sentani dan Perbukitan Teletubbies Jayapura",
        "Danau Sentani di Jayapura, Papua, membentang megah di bawah lereng Pegunungan Cycloop. Danau air tawar seluas lebih dari 9.000 hektar ini dihiasi puluhan pulau kecil dan perkampungan terapung suku asli Sentani yang terampil membuat lukisan kulit kayu khas. Bukit Tungkuwiri di tepian danau menyajikan pemandangan padang rumput hijau bergelombang.",
        "Jayapura, Papua",
        "Wisata Alam",
        "danau-sentani-jayapura-papua",
    ),
    (
        "Pesona Pantai Liang dan Pasir Putih Ambon Maluku",
        "Pantai Liang atau Pantai Hunimua di Maluku Tengah dinobatkan sebagai salah satu pantai terindah di Indonesia oleh badan PBB. Memiliki air laut bergradasi toska dan biru dongker yang jernih luar biasa, hamparan pasir putih pantai yang luas dinaungi oleh pepohonan rindang tempat bersantai menikmati semilir angin laut Banda.",
        "Maluku Tengah, Maluku",
        "Wisata Bahari",
        "pantai-liang-ambon",
    ),
    (
        "Menyusuri Jejak Kejayaan Pala di Kepulauan Banda Neira Maluku",
        "Banda Neira di Maluku Tengah adalah pulau bersejarah yang pernah menjadi satu-satunya penghasil rempah buah pala di dunia yang diperebutkan bangsa Eropa. Di pulau ini berdiri Benteng Belgica peninggalan VOC Belanda yang menghadap ke laut lepas berlatar kerucut megah Gunung Api Banda. Wisatawan dapat menyelam di terumbu karang lava flow yang tumbuh subur pasca letusan gunung api.",
        "Maluku Tengah, Maluku",
        "Wisata Sejarah",
        "kepulauan-banda-neira",
    ),
    (
        "Keindahan Tebing Karang Piaynemo Ikon Eksotis Raja Ampat",
        "Piaynemo merupakan salah satu gugusan bukit karang karst paling terkenal di Kepulauan Raja Ampat. Setelah menaiki sekitar 300 anak tangga kayu menuju gardu pandang di puncak bukit, wisatawan disuguhkan panorama pulau-pulau karang kecil yang mengapung di atas laguna berair hijau zamrud dan biru safir.",
        "Raja Ampat, Papua Barat Daya",
        "Wisata Bahari",
        "piaynemo-raja-ampat",
    ),
    (
        "Pesona Pasir Halus Selembut Tepung di Pantai Ngurbloat Kepulauan Kei",
        "Pantai Ngurbloat atau Pantai Pasir Panjang di Pulau Kei Kecil, Maluku Tenggara, dinobatkan oleh National Geographic sebagai pantai dengan pasir paling halus di dunia, dengan tekstur yang menyerupai tepung terigu. Garis pantainya membentang sepanjang 3 kilometer dinaungi jajaran pohon kelapa dengan air laut yang sangat jernih dan tenang.",
        "Maluku Tenggara, Maluku",
        "Wisata Bahari",
        "pantai-ngurbloat-kepulauan-kei",
    ),
    (
        "Keunikan Tradisi Mumi dan Festival Lembah Baliem Wamena",
        "Lembah Baliem di Kabupaten Jayawijaya, Papua Pegunungan, berada di ketinggian 1.600 meter diapit pegunungan Jayawijaya yang bersuhu dingin. Kawasan ini dihuni oleh suku Dani, Lani, dan Yali yang mempertahankan tradisi adat leluhur dan rumah honai tradisional. Di desa Jiwika dan Sompaima tersimpan mumi panglima perang berumur ratusan tahun yang diawetkan secara alami.",
        "Jayawijaya, Papua Pegunungan",
        "Wisata Budaya",
        "lembah-baliem-wamena",
    ),
]

# Supplementary travel destination themes and regional loci to synthesize authentic 660 unique articles
REGIONAL_EXPANSIONS = [
    # (Region, Province, Terrain, Focus, Keywords)
    ("Sentul", "Bogor, Jawa Barat", "pegunungan", "curug dan trekking", ["leuwi", "hejo", "barong", "cepeng", "cibaliung", "love", "kencana", "pari"]),
    ("Puncak & Cisarua", "Bogor, Jawa Barat", "perbukitan teh", "hawa dingin dan villa", ["telaga", "saat", "warna", "cilember", "panjang", "agrowisata", "gunung mas"]),
    ("Ciwidey & Pangalengan", "Bandung, Jawa Barat", "danau belerang dan kebun teh", "kawah dan camping", ["patuha", "ranca upas", "situ cileunca", "wayang windu", "nimo", "cukul"]),
    ("Lembang & Parongpong", "Bandung Barat, Jawa Barat", "hutan pinus dan curug", "wisata keluarga dan edukasi", ["maribaya", "curug cimahi", "tangkuban parahu", "orchid forest", "cikole", "jayagiri"]),
    ("Geopark Ciletuh", "Sukabumi, Jawa Barat", "amfiteater alam dan pantai", "curug purba dan tebing", ["cikaso", "cimarinjung", "awang", "sodong", "puncak darma", "palabuhanratu"]),
    ("Garut Selatan & Cipanas", "Garut, Jawa Barat", "gunung api dan pemandian air panas", "kawah dan kebun teh", ["papandayan", "guntur", "talaga bodas", "darajat pass", "santolo", "sayang heulang"]),
    ("Pangandaran & Ciamis", "Pangandaran, Jawa Barat", "pantai dan ngarai sungai", "body rafting dan cagar alam", ["batukaras", "madasari", "green canyon", "ciwayang", "batu hiu", "pananjung"]),
    ("Kuningan & Majalengka", "Kuningan, Jawa Barat", "lereng Gunung Ciremai", "telaga jernih dan terasering", ["talaga remis", "curug ciputrawangi", "panyaweuyan", "situ cipanten", "palutungan"]),
    ("Anyer & Ujung Kulon", "Pandeglang, Banten", "pantai selat sunda dan suaka badak", "konservasi dan bahari", ["pulau peucang", "tanjung lesung", "pantai carita", "ciputih", "handeuleum"]),
    ("Kepulauan Seribu", "DKI Jakarta", "pulau karang dan pasir putih", "snorkeling dan diving", ["pulau pari", "pulau pramuka", "pulau harapan", "pulau tidung", "pulau macan", "sepa"]),
    ("Dataran Tinggi Dieng", "Wonosobo, Jawa Tengah", "negeri di atas awan", "candi dan kawah belerang", ["sikunir", "telaga warna", "kawah sikidang", "candi arjuna", "telaga cebong", "prau"]),
    ("Karimunjawa", "Jepara, Jawa Tengah", "kepulauan tropis laut jawa", "snorkeling karang dan hiu", ["menjangan besar", "menjangan kecil", "tanjung gelam", "pulau cilik", "cemara"]),
    ("Magelang & Borobudur", "Magelang, Jawa Tengah", "lembah perbukitan menoreh", "candi budha dan arung jeram", ["punthuk setumbu", "candi mendut", "candi pawon", "sungai elo", "silancur highland"]),
    ("Gunungkidul", "D.I. Yogyakarta", "pantai tebing karst", "pasir putih dan goa", ["pantai indrayanti", "drini", "pok tunggal", "timang", "ngranahan", "jomblang", "ngobaran"]),
    ("Bantul & Kulon Progo", "D.I. Yogyakarta", "hutan pinus dan gumuk pasir", "sunset dan wisata alam", ["hutan pinus mangunan", "becici", "pengger", "kalibiru", "waduk sermo", "pantai glagah"]),
    ("Banyuwangi", "Jawa Timur", "ujung timur pulau jawa", "kawah ijen dan pantai peselancar", ["g-land plengkung", "teluk hijau", "djawatan benculuk", "pantai boom", "bangsring underwater"]),
    ("Bromo & Semeru", "Probolinggo, Jawa Timur", "kaldera tengger", "lautan pasir dan sunrise", ["penanjakan satu", "pasir berbisik", "bukit teletubbies", "coban rondo", "coban talun", "ranu kumbolo"]),
    ("Malang Selatan", "Malang, Jawa Timur", "deretan pantai samudra hindia", "pulau karang dan teluk", ["pantai balekambang", "pantai goa cina", "tiga warna", "pantai sendiki", "kondang merak"]),
    ("Pacitan", "Pacitan, Jawa Timur", "kota seribu satu goa", "pantai tebing dan selancar", ["pantai klayar", "pantai banyu tibo", "goa gong", "goa tabuhan", "pantai srau", "kasap"]),
    ("Badung & Kuta", "Badung, Bali", "pusat pariwisata bali", "pantai sunset dan surf", ["pantai pandawa", "melasti", "padang padang", "dreamland", "seminyak", "canggu", "bingin"]),
    ("Gianyar & Ubud", "Gianyar, Bali", "pusat seni dan budaya bali", "hutan kera dan lembah", ["monkey forest ubud", "campuhan ridge walk", "goa gajah", "tirta empul", "blangsinga"]),
    ("Nusa Penida & Lembongan", "Klungkung, Bali", "pulau karang terpisah", "tebing curam dan pantai perawan", ["kelingking beach", "broken beach", "angels billabong", "crystal bay", "diamond beach", "atuh"]),
    ("Buleleng & Bali Utara", "Buleleng, Bali", "lumba-lumba dan air terjun", "hawa sejuk dan pantai tenang", ["pantai lovina", "air terjun gitgit", "sekumpul waterfalls", "danau tamblingan", "buyan"]),
    ("Lombok Barat & Gili", "Lombok Barat, NTB", "tiga gili legendaris", "bebas kendaraan bermotor", ["gili trawangan", "gili meno", "gili air", "pantai senggigi", "bukit malimbu"]),
    ("Lombok Selatan & Mandalika", "Lombok Tengah, NTB", "sirkuit internasional dan teluk", "pantai pasir merica", ["pantai kuta mandalika", "tanjung aan", "pantai mawun", "pantai selong belanak", "merese"]),
    ("Labuan Bajo & Komodo", "Manggarai Barat, NTT", "gerbang pulau komodo", "pulau karst dan diving kelas dunia", ["pulau padar", "pulau rinca", "pink beach", "manta point", "gua batu cermin", "amelia"]),
    ("Flores & Sumba", "Nusa Tenggara Timur", "desa megalitikum dan savana", "danau kelimutu dan tenun ikat", ["wae rebo", "kampung bena", "pantai walakiri", "air terjun tanggedu", "bukit wairinding"]),
    ("Danau Toba & Karo", "Sumatera Utara", "kaldera vulkanik terbesar", "rumah bolon dan air terjun", ["pulau samosir", "tongging", "berastagi", "taman simalem", "huta siallagan", "tuk tuk"]),
    ("Bukittinggi & Harau", "Sumatera Barat", "ngarai batu granit dan danau", "kuliner minang dan arsitektur", ["danau maninjau", "danau singkarak", "kelok sembilan", "puncak lawang", "istano basa pagaruyung"]),
    ("Bangka & Belitung", "Kepulauan Bangka Belitung", "batu granit dan laskar pelangi", "pantai tenang dan pulau mercusuar", ["pantai parai tenggiri", "pulau lengkuas", "tanjung tinggi", "danau kaolin", "punai"]),
    ("Lampung & Krakatau", "Lampung", "pesisir selatan sumatera", "lumba-lumba dan gajah sumatera", ["pantai gigi hiu", "pulau kelagian", "krakatau", "way kambas", "pantai mutun"]),
    ("Toraja & Maros", "Sulawesi Selatan", "budaya leluhur dan karst purba", "tongkonan dan gua prasejarah", ["leang leang", "londa", "pallawa", "batutumonga", "tilanga", "kete kesu"]),
    ("Manado & Bunaken", "Sulawesi Utara", "taman laut dan gunung berapi", "diving dinding karang dan kuliner", ["pulau siladen", "danau linow", "gunung lokon", "pantai malalayang", "pulau manado tua"]),
    ("Wakatobi & Buton", "Sulawesi Tenggara", "segitiga terumbu karang", "suku bajo dan benteng kraton", ["pulau tomiya", "pulau hoga", "pulau binongko", "benteng keraton buton", "pantai nirwana"]),
    ("Derawan & Berau", "Kalimantan Timur", "kepulauan atol dan danau purba", "penyu hijau dan ubur-ubur", ["pulau maratua", "pulau sangalaki", "danau haji buang", "labuan cermin", "kehe daing"]),
    ("Banda Neira & Kei", "Maluku", "pulau rempah dan pantai tepung", "benteng belgica dan pasir panjang", ["pulau hatta", "pulau pisang", "pantai bair", "gua hawang", "benteng nassau", "gunung api banda"]),
    ("Raja Ampat", "Papua Barat Daya", "surga bahari khatulistiwa", "karst toska dan pari manta", ["misool", "wayag", "telaga bintang", "friwen wall", "kali biru warsambin", "sauwandarek"]),
    ("Sentani & Wamena", "Papua", "lembah pegunungan tengah", "danau air tawar dan festival budaya", ["bukit teletubbies tungkuwiri", "pulau asei", "lembah baliem", "pasir putih wamena", "danau habema"]),
]


def generate_extended_catalog() -> List[Dict[str, Any]]:
    """Synthesize clean, unique destination articles matching portal profiles.

    Produces ~660 unique articles distributed as:
    - ~250 NativeIndonesia articles (heavy nature, waterfalls, beaches, mountain trekking)
    - ~230 IndonesiaTravel articles (official ministry, priority destinations, cultural heritage)
    - ~180 Wisato articles (travel spotlights, hidden gems, culinary, eco-tours)
    """
    articles: List[Dict[str, Any]] = []
    seen_titles = set()

    # 1. Ingest core handmade articles first
    for title, content, location, category, slug in CORE_DESTINATIONS:
        doc_id = f"wisata_{len(articles) + 1:03d}"
        # Determine appropriate source matching design
        if "nativeindonesia" in slug or "curug" in slug or "kawah" in slug or "belerang" in slug:
            source = "nativeindonesia"
        elif "candi" in slug or "taman-nasional" in slug or "danau-toba" in slug or "raja-ampat" in slug:
            source = "indonesiatravel"
        else:
            source = "wisato"
        doc = _build_article(title, content, location, category, source, slug, doc_id)
        articles.append(doc)
        seen_titles.add(title.strip().lower())

    # 2. Procedural expansion covering every region systematically
    themes = [
        (
            "Pesona Wisata Alam Eksotis {spot} di {region}",
            "Kawasan wisata alam {spot} yang terletak di {region}, {prov} menyajikan panorama alam yang asri dan udara yang sejuk. Lanskap perbukitan dan vegetasi hijau tropis di kawasan ini sangat cocok bagi wisatawan yang ingin melepaskan penat dari hiruk-pikuk perkotaan. Jalur setapak menuju lokasi telah tertata rapi dengan berbagai spot foto dengan latar belakang perbukitan yang menawan.",
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

    # Count existing
    for doc in articles:
        source_counts[doc["source"]] += 1

    # Desired caps: NativeIndonesia ~250, IndonesiaTravel ~230, Wisato ~180
    source_caps = {"nativeindonesia": 250, "indonesiatravel": 230, "wisato": 180}

    reg_idx = 0
    theme_idx = 0
    spot_idx = 0

    while len(articles) < target_total:
        reg_info = REGIONAL_EXPANSIONS[reg_idx % len(REGIONAL_EXPANSIONS)]
        region_name, prov_name, terrain, focus_name, spots = reg_info
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
            slug = re.sub(r"[^a-z0-9]+", "-", f"{spot_name}-{region_name}").strip("-").lower()
            doc_id = f"wisata_{len(articles) + 1:03d}"

            doc = _build_article(
                title=title,
                content=content,
                location=prov_name,
                category=cat,
                source=chosen_source,
                slug=slug,
                doc_id=doc_id,
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
    """Build raw corpus containing 700 documents:

    - 660 unique authentic travel destination articles
    - 40 deliberate duplicates/near-duplicates:
      * 20 exact duplicates (identical normalized text hash)
      * 20 near-duplicates (>95% text similarity with slight CMS modifications)
    Returns:
        (raw_corpus_documents, deliberate_duplicate_records)
    """
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
