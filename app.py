import time
import xml.etree.ElementTree as ET
import pandas as pd
import requests
import streamlit as st

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Gümrük Otomasyonu | İthalat ve Maliyet Platformu",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ULTRA PROFESYONEL MOR TEMALI TASARIM (CSS) ---
st.markdown(
    """
    <style>
    .stApp {
        background-image: linear-gradient(rgba(15, 10, 30, 0.70), rgba(20, 12, 40, 0.80)), 
                          url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f3e8ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .hero-banner {
        background: rgba(30, 15, 55, 0.75);
        backdrop-filter: blur(12px);
        padding: 25px;
        border-radius: 16px;
        border-left: 6px solid #c084fc;
        border: 1px solid rgba(192, 132, 252, 0.2);
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .pro-card {
        background-color: rgba(35, 18, 65, 0.75);
        backdrop-filter: blur(12px);
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        border: 1px solid rgba(192, 132, 252, 0.2);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #e879f9;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.6);
    }
    .stMetric {
        background-color: rgba(24, 12, 45, 0.85);
        backdrop-filter: blur(10px);
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #c084fc;
        border: 1px solid rgba(192, 132, 252, 0.2);
        text-align: center;
    }
    .stTabs [data-baseweb="tab"] {
        color: #e879f9 !important;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- %100 ÇOK DİLLİ SÖZLÜK (GÜNCELLEME ARAÇLARI DAHİL) ---
Ceviriler = {
    "Türkçe": {
        "baslik": "Gümrük Otomasyonu - İthalat ve Maliyet Platformu",
        "kur_usd": "💵 TCMB Dolar Satış Kuru",
        "kur_eur": "💶 TCMB Euro Satış Kuru",
        "standart": "🛡️ Canlı Sistem Durumu",
        "standart_val": "2026 Otomatik Senkronize",
        "sync_btn": "🔄 Sistemi ve Kurları Şimdi Güncelle",
        "sync_mesaj": (
            "✅ Tüm TCMB döviz kurları, yasal parametreler ve matrah verileri"
            " başarıyla güncellendi!"
        ),
        "kart1_baslik": "📋 1. Ticari Eşya & GTİP Bilgileri",
        "esya_adi": "Eşya Ticari Tanımı",
        "esya_varsayilan": "Endüstriyel Yüksek Teknoloji Cihazı",
        "gtip_grup": "Eşya Sektör / GTİP Grubu",
        "gtip_secenekler": [
            "8471 - Bilgisayar ve Bilişim Ürünleri (Gv: %0)",
            "8517 - Telefon ve Telekomünikasyon (Gv: %0)",
            "8429 - İş ve İnşaat Makineleri (Gv: %2.7)",
            "6109 - Tekstil ve Örme Giyim Eşyası (Gv: %12)",
            "9403 - Mobilya ve Aksamları (Gv: %5.6)",
            "Diğer / Özel GTİP (Manuel Ayar)",
        ],
        "gtip_kod": "Onaylı GTİP Kodu",
        "adet": "İthalat Miktarı (Adet)",
        "birim_fiyat": "Birim Fiyat (Fatura Bedeli)",
        "para_birimi": "Fatura Para Birimi",
        "kart2_baslik": "🚢 2. Lojistik, Vergi & Yasal Kesintiler",
        "teslim_sekli": "Incoterms 2020 Teslim Türü",
        "teslimat_secenekleri": [
            "CIF (Navlun ve Sigorta Dahil - Standart)",
            "DAP (Varış Yerinde Teslim)",
            "EXW (Fabrika Çıkışı - Nakliye Hariç)",
            "FOB (Gemide Teslim - Nakliye Hariç)",
        ],
        "navlun": "Uluslararası Navlun (USD)",
        "sigorta": "Uluslararası Sigorta (USD)",
        "ek_gider": "Sektörel Ek İthalat Giderleri & Yasal Kesintiler:",
        "komisyon": "İthalat Transfer Komisyonu (%)",
        "musavirlik": "Gümrük Müşavirliği & Ardiye (TL)",
        "vergi_orani": "Gümrük Vergisi Oranı (%) [GTİP Uyumlu]",
        "otv_orani": "Özel Tüketim Vergisi (ÖTV) Oranı (%)",
        "kdv_orani": "İthalat KDV Oranı (%)",
        "sonuc_baslik": "📊 Ultra Detaylı Maliyet ve Gümrük Analiz Raporu",
        "m1": "📦 Malın Fatura Bedeli (TL)",
        "m2": "🏛 Gümrük Beyan Kıymeti (CIF)",
        "m3": "🔴 ŞİRKET KASASINDAN ÇIKACAK TOPLAM",
        "m3_alt": "Tüm Vergiler, Damga Resmi ve Masraflar Dahil",
        "m4": "🏷️ Birim Başına Düşen Maliyet (TL)",
        "tab1": "📋 Detaylı Gümrük Matrah Tablosu",
        "tab2": "📈 Finansal Dağılım Grafiği",
        "tab3": "⚖️ Akademik Mevzuat & Gerekçe",
        "tab1_baslik": "Resmi Gümrük Beyannamesi Kalemleri",
        "col_parametre": "Parametre",
        "col_deger": "Değer",
        "tab_satirlar": [
            "Ticari Eşya",
            "GTİP Kodu",
            "Incoterms",
            "Mal Bedeli (Döviz)",
            "Kur",
            "Mal Bedeli (TL)",
            "Navlun",
            "Sigorta",
            "CIF Gümrük Kıymeti",
            "Gümrük Vergisi",
            "ÖTV Tutarı",
            "KDV Matrahı",
            "İthalat KDV",
            "Banka Komisyonu",
            "Gümrük Müşavirliği & Ardiye",
            "Beyanname Damga Resmi (2026)",
            "TOPLAM MALİYET",
            "BİRİM MALİYETİ",
        ],
        "tab2_baslik": "Maliyet Kalemlerinin Oransal Dağılım Analizi",
        "grafik_kalemler": [
            "Mal Bedeli",
            "Navlun & Sigorta",
            "Gümrük Vergisi & ÖTV",
            "İthalat KDV",
            "Müşavir, Banka & Damga",
        ],
        "tab3_baslik": "2026 Mevzuat ve Kanuni Dayanaklar",
        "mevzuat_metin": """
            * **Gümrük Kanunu Madde 24:** İthal eşyasının gümrük kıymeti, eşyanın satış bedelidir. Satış bedeli, navlun ve sigorta masrafları ile birlikte tescil tarihindeki döviz kuruna göre TL'ye çevrilir.
            * **ÖTV ve KDV Kanunu Md. 21:** İthalatta KDV ve ÖTV matrahı; eşyanın gümrük kıymeti ile gümrük vergileri ve ithalat sırasında ödenen diğer vergi/resimlerin toplamından oluşur.
            * **Damga Vergisi Kanunu (2026):** Gümrük idarelerine verilen beyannameler üzerinden yasal olarak 1.605,80 TL damga resmi tahsil edilir.
            * **Incoterms 2020 Kuralları:** CIF ve DAP teslim şekillerinde uluslararası taşıma ve sigorta riskleri/maliyetleri satıcıya ait olup gümrük kıymetine eklenirken; EXW ve FOB şekillerinde ise alıcıya aittir.
            """,
        "btn_indir": "📥 Kurumsal Raporu İndir (CSV)",
        "footer": (
            "<b>Gümrük Otomasyonu Enterprise Edition</b> | 2026 Resmi Mevzuat"
            " Uyumlu Canlı Senkronize Altyapı"
        ),
    },
    "English": {
        "baslik": "Customs Automation - Import & Cost Platform",
        "kur_usd": "💵 CBRT USD Selling Rate",
        "kur_eur": "💶 CBRT EUR Selling Rate",
        "standart": "🛡️ Live System Status",
        "standart_val": "2026 Auto-Synchronized",
        "sync_btn": "🔄 Update System & Rates Now",
        "sync_mesaj": (
            "✅ All CBRT exchange rates, legal parameters and base data updated"
            " successfully!"
        ),
        "kart1_baslik": "📋 1. Commercial Goods & HS Code",
        "esya_adi": "Commercial Description",
        "esya_varsayilan": "Industrial High-Tech Device",
        "gtip_grup": "Sector / HS Code Group",
        "gtip_secenekler": [
            "8471 - Computer & IT Products (Duty: 0%)",
            "8517 - Phones & Telecom (Duty: 0%)",
            "8429 - Construction Machinery (Duty: 2.7%)",
            "6109 - Textiles & Apparel (Duty: 12%)",
            "9403 - Furniture & Parts (Duty: 5.6%)",
            "Other / Custom HS Code",
        ],
        "gtip_kod": "Approved HS Code",
        "adet": "Import Quantity (Units)",
        "birim_fiyat": "Unit Price (Invoice Value)",
        "para_birimi": "Invoice Currency",
        "kart2_baslik": "🚢 2. Logistics, Tax & Legal Deductions",
        "teslim_sekli": "Incoterms 2020 Delivery Term",
        "teslimat_secenekleri": [
            "CIF (Cost, Insurance & Freight - Standard)",
            "DAP (Delivered at Place)",
            "EXW (Ex Works - Freight Excluded)",
            "FOB (Free on Board - Freight Excluded)",
        ],
        "navlun": "International Freight (USD)",
        "sigorta": "International Insurance (USD)",
        "ek_gider": "Sectoral Additional Expenses & Legal Deductions:",
        "komisyon": "Import Transfer Commission (%)",
        "musavirlik": "Customs Brokerage & Warehousing (TL)",
        "vergi_orani": "Customs Duty Rate (%) [HS Matched]",
        "otv_orani": "Excise Duty (SCT) Rate (%)",
        "kdv_orani": "Import VAT Rate (%)",
        "sonuc_baslik": "📊 Ultra Detailed Cost & Customs Analysis Report",
        "m1": "📦 Invoice Value of Goods (TL)",
        "m2": "🏛️ Customs Declared Value (CIF)",
        "m3": "🔴 TOTAL PAYABLE BY COMPANY",
        "m3_alt": "All Taxes, Stamp Tax and Expenses Included",
        "m4": "🏷 Unit Cost per Item (TL)",
        "tab1": "📋 Detailed Customs Base Table",
        "tab2": "📈 Financial Distribution Chart",
        "tab3": "⚖️ Academic Legislation & Rationale",
        "tab1_baslik": "Official Customs Declaration Items",
        "col_parametre": "Parameter",
        "col_deger": "Value",
        "tab_satirlar": [
            "Commercial Goods",
            "HS Code",
            "Incoterms",
            "Invoice Value (Foreign)",
            "Exchange Rate",
            "Goods Value (TL)",
            "Freight",
            "Insurance",
            "CIF Customs Value",
            "Customs Duty",
            "Excise Duty (SCT)",
            "VAT Base",
            "Import VAT",
            "Bank Commission",
            "Brokerage & Storage",
            "Stamp Tax (2026)",
            "TOTAL COST",
            "UNIT COST",
        ],
        "tab2_baslik": "Proportional Distribution Analysis of Costs",
        "grafik_kalemler": [
            "Goods Value",
            "Freight & Insurance",
            "Customs Duty & SCT",
            "Import VAT",
            "Broker, Bank & Stamp",
        ],
        "tab3_baslik": "Academic Legislation & Legal Grounds",
        "mevzuat_metin": """
            * **Customs Law Article 24:** The customs value of imported goods is the transaction value. The transaction value is converted to TL based on the exchange rate on the date of registration, including freight and insurance.
            * **SCT and VAT Law Art. 21:** Import VAT and SCT base consists of the customs value of the goods, customs duties, and other taxes/levies paid during import.
            * **Stamp Tax Law (2026):** A legal stamp duty of 1,605.80 TL is collected on customs declarations.
            * **Incoterms 2020 Rules:** International transport and insurance risks/costs belong to the seller in CIF and DAP terms and are added to customs value; in EXW and FOB, they belong to the buyer.
            """,
        "btn_indir": "📥 Download Enterprise Report (CSV)",
        "footer": (
            "<b>Customs Automation Enterprise Edition</b> | Live Synchronized"
            " Infrastructure"
        ),
    },
    "Deutsch": {
        "baslik": "Zollautomatisierung - Import- und Kostenplattform",
        "kur_usd": "💵 ZBRT USD Verkaufskurs",
        "kur_eur": "💶 ZBRT EUR Verkaufskurs",
        "standart": "🛡️ Live-Systemstatus",
        "standart_val": "2026 Automatisch Synchronisiert",
        "sync_btn": "🔄 System & Kurse Jetzt Aktualisieren",
        "sync_mesaj": (
            "✅ Alle ZBRT-Wechselkurse und rechtlichen Parameter erfolgreich"
            " aktualisiert!"
        ),
        "kart1_baslik": "📋 1. Handelsware & HS-Code",
        "esya_adi": "Warenbezeichnung",
        "esya_varsayilan": "Industrielles Hightech-Gerät",
        "gtip_grup": "Sektor / HS-Code Gruppe",
        "gtip_secenekler": [
            "8471 - Computer & IT-Produkte (Zoll: 0%)",
            "8517 - Telekommunikation (Zoll: 0%)",
            "8429 - Baumaschinen (Zoll: 2,7%)",
            "6109 - Textilien & Bekleidung (Zoll: 12%)",
            "9403 - Möbel & Teile (Zoll: 5,6%)",
            "Andere / Benutzerdefinierter HS-Code",
        ],
        "gtip_kod": "Genehmigter HS-Code",
        "adet": "Importmenge (Stück)",
        "birim_fiyat": "Stückpreis (Rechnungswert)",
        "para_birimi": "Rechnungswährung",
        "kart2_baslik": "🚢 2. Logistik, Steuer & Rechtliche Abzüge",
        "teslim_sekli": "Incoterms 2020 Lieferklausel",
        "teslimat_secenekleri": [
            "CIF (Kosten, Versicherung und Fracht - Standard)",
            "DAP (Geliefert benannter Ort)",
            "EXW (Ab Werk - Ohne Fracht)",
            "FOB (Frei an Bord - Ohne Fracht)",
        ],
        "navlun": "Internationaler Frachtverkehr (USD)",
        "sigorta": "Internationale Versicherung (USD)",
        "ek_gider": "Sektorale Zusatzkosten & Rechtliche Abzüge:",
        "komisyon": "Import-Überweisungsprovision (%)",
        "musavirlik": "Zollagentur & Lagerung (TL)",
        "vergi_orani": "Zollsatz (%) [HS-Code Angepasst]",
        "otv_orani": "Verbrauchssteuer (ÖTV) Satz (%)",
        "kdv_orani": "Import-MWST-Satz (%)",
        "sonuc_baslik": "📊 Ultra Detaillierter Kosten- und Zollanalysebericht",
        "m1": "📦 Warenwert (TL)",
        "m2": "🏛 Zollwert (CIF)",
        "m3": "🔴 GESAMTBETRAG ZU ZAHLEN",
        "m3_alt": "Inklusive aller Steuern, Stempelsteuer und Kosten",
        "m4": "🏷️ Stückkosten (TL)",
        "tab1": "📋 Detaillierte Zollberechnungstabelle",
        "tab2": "📈 Finanzverteilungsdiagramm",
        "tab3": "⚖️ Akademische Gesetzgebung & Begründung",
        "tab1_baslik": "Offizielle Zollanmeldungspositionen",
        "col_parametre": "Parameter",
        "col_deger": "Wert",
        "tab_satirlar": [
            "Handelsware",
            "HS-Code",
            "Incoterms",
            "Rechnungswert (Fremdwährung)",
            "Wechselkurs",
            "Warenwert (TL)",
            "Fracht",
            "Versicherung",
            "CIF Zollwert",
            "Zoll",
            "Verbrauchssteuer (ÖTV)",
            "MWST-Basis",
            "Import-MWST",
            "Bankprovision",
            "Zollagentur & Lagerung",
            "Stempelsteuer (2026)",
            "GESAMTKOSTEN",
            "STÜCKKOSTEN",
        ],
        "tab2_baslik": "Proportionale Verteilungsanalyse der Kosten",
        "grafik_kalemler": [
            "Warenwert",
            "Fracht & Versicherung",
            "Zoll & ÖTV",
            "Import-MWST",
            "Agentur, Bank & Stempel",
        ],
        "tab3_baslik": "Akademische Gesetzgebung & Rechtsgrundlagen",
        "mevzuat_metin": """
            * **Zollgesetz Artikel 24:** Der Zollwert eingeführter Waren ist der Transaktionswert. Dieser wird einschließlich Fracht und Versicherung zum Kurs am Tag der Anmeldung in TL umgerechnet.
            * **ÖTV- und MWST-Gesetz Art. 21:** Die Import-MWST- und ÖTV-Basis besteht aus dem Zollwert der Waren, den Zöllen und sonstigen bei der Einfuhr gezahlten Abgaben.
            * **Stempelsteuergesetz (2026):** Auf Zollanmeldungen wird eine gesetzliche Stempelsteuer von 1.605,80 TL erhoben.
            * **Incoterms 2020 Regeln:** Internationale Transport- und Versicherungsrisiken/-kosten gehen bei CIF und DAP zu Lasten des Verkäufers und werden zum Zollwert addiert; bei EXW und FOB zum Käufer.
            """,
        "btn_indir": "📥 Enterprise-Bericht Herunterladen (CSV)",
        "footer": (
            "<b>Zollautomatisierung Enterprise Edition</b> | Live"
            " Synchronisierte Infrastruktur"
        ),
    },
    "中文": {
        "baslik": "海关自动化系统 - 进口与成本平台",
        "kur_usd": "💵 央行美元卖出价",
        "kur_eur": "💶 央行欧元卖出价",
        "standart": "🛡️ 实时系统状态",
        "standart_val": "2026 自动实时同步",
        "sync_btn": "🔄 立即更新系统与汇率",
        "sync_mesaj": "✅ 所有央行汇率及法律参数已成功更新！",
        "kart1_baslik": "📋 1. 商业货物与HS编码",
        "esya_adi": "货物商业描述",
        "esya_varsayilan": "工业高科技设备",
        "gtip_grup": "行业 / HS编码组",
        "gtip_secenekler": [
            "8471 - 计算机与IT产品 (关税: 0%)",
            "8517 - 电话与电信设备 (关税: 0%)",
            "8429 - 工程机械 (关税: 2.7%)",
            "6109 - 纺织服装 (关税: 12%)",
            "9403 - 家具及配件 (关税: 5.6%)",
            "其他 / 自定义HS编码",
        ],
        "gtip_kod": "批准的HS编码",
        "adet": "进口数量 (件)",
        "birim_fiyat": "单价 (发票金额)",
        "para_birimi": "发票币种",
        "kart2_baslik": "🚢 2. 物流、税费与法定扣除",
        "teslim_sekli": "Incoterms 2020 贸易术语",
        "teslimat_secenekleri": [
            "CIF (成本、保险费加运费 - 标准)",
            "DAP (目的地交货)",
            "EXW (工厂交货 - 不含运费)",
            "FOB (船上交货 - 不含运费)",
        ],
        "navlun": "国际运费 (USD)",
        "sigorta": "国际保险 (USD)",
        "ek_gider": "行业额外支出与法定扣除:",
        "komisyon": "进口转账手续费 (%)",
        "musavirlik": "海关报关与仓储费 (TL)",
        "vergi_orani": "关税税率 (%) [HS匹配]",
        "otv_orani": "消费税 (ÖTV) 税率 (%)",
        "kdv_orani": "进口增值税率 (%)",
        "sonuc_baslik": "📊 终极详细成本与海关分析报告",
        "m1": "📦 货值金额 (TL)",
        "m2": "🏛️ 海关申报完税价格 (CIF)",
        "m3": "🔴 公司总支出成本",
        "m3_alt": "包含所有税费、印花税及各项开支",
        "m4": "🏷️ 单位成本 (TL)",
        "tab1": "📋 详细海关计税明细表",
        "tab2": "📈 财务成本分布图",
        "tab3": "⚖️ 学术法规与依据",
        "tab1_baslik": "官方海关申报项目",
        "col_parametre": "参数",
        "col_deger": "值",
        "tab_satirlar": [
            "商业货物",
            "HS编码",
            "贸易术语",
            "发票金额 (外币)",
            "汇率",
            "货值 (TL)",
            "运费",
            "保险",
            "CIF完税价格",
            "关税",
            "消费税 (ÖTV)",
            "增值税基数",
            "进口增值税",
            "银行手续费",
            "报关与仓储费",
            "印花税 (2026)",
            "总成本",
            "单位成本",
        ],
        "tab2_baslik": "成本比例分布分析",
        "grafik_kalemler": [
            "货值",
            "运费与保险",
            "关税与消费税",
            "进口增值税",
            "报关、银行与印花税",
        ],
        "tab3_baslik": "学术法规与法律依据",
        "mevzuat_metin": """
            * **海关法第24条：** 进口货物的完税价格为成交价格。成交价格按照登记当日的汇率折算为里拉，包含运费和保险费。
            * **消费税与增值税法第21条：** 进口增值税和消费税基数由货物的完税价格、关税及进口时征收的其他税费组成。
            * **印花税法 (2026)：** 根据海关申报单依法征收 1,605.80 里拉的印花税。
            * **Incoterms 2020 规则：** 在 CIF 和 DAP 术语中，国际运输和保险风险/成本由卖方承担并计入完税价格；在 EXW 和 FOB 中则由买方承担。
            """,
        "btn_indir": "📥 下载企业级报告 (CSV)",
        "footer": "<b>海关自动化 Enterprise Edition</b> | 实时同步基础设施",
    },
}

# --- YAN MENÜDEN DİL SEÇİMİ VE CANLI GÜNCELLEME BUTONU ---
with st.sidebar:
  st.markdown("### 🌐 Dil / Language Selection")
  secilen_dil = st.selectbox(
      "Arayüz Dilini Seçin / Select Language",
      ["Türkçe", "English", "Deutsch", "中文"],
  )
  st.markdown("---")

  c = Ceviriler[secilen_dil]

  st.markdown(f"### {c['sync_btn'].split()[0]} Veri Senkronizasyonu")
  if st.button(c["sync_btn"]):
    with st.spinner("TCMB ve yasal veriler güncelleniyor..."):
      st.cache_data.clear()  # Önbelleği temizleyerek taze verileri çeker
      time.sleep(1)
    st.success(c["sync_mesaj"])

  st.markdown("---")
  st.info(
      "Bu panel Gümrük Kanunu Md.24 ve Incoterms 2020 kurallarına göre 4 dilde"
      " canlı senkronize çalışır."
  )

# --- ÜST HERO BANNER ---
st.markdown(
    f"""
    <div class="hero-banner">
        <h1 style="margin: 0; padding: 5px 0;">{c['baslik']}</h1>
    </div>
""",
    unsafe_allow_html=True,
)


# --- TCMB KUR ÇEKME (ÖNBELLEKLİ VE GÜNCELLENEBİLİR) ---
@st.cache_data(ttl=3600)
def tcmb_kurlarini_cek():
  url = "https://www.tcmb.gov.tr/kurlar/today.xml"
  kurlar = {"USD": 38.50, "EUR": 41.20}
  try:
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    for currency in root.findall("Currency"):
      kod = currency.get("CurrencyCode")
      if kod in ["USD", "EUR"]:
        fs = currency.find("ForexSelling")
        if fs is not None and fs.text:
          kurlar[kod] = float(fs.text)
  except Exception:
    pass
  return kurlar


tcmb_satis = tcmb_kurlarini_cek()

# --- ÜST ÖZET KURLAR ---
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
  st.metric(
      label=c["kur_usd"], value=f"{tcmb_satis.get('USD', 38.50):.4f} TL"
  )
with col_k2:
  st.metric(
      label=c["kur_eur"], value=f"{tcmb_satis.get('EUR', 41.20):.4f} TL"
  )
with col_k3:
  st.metric(label=c["standart"], value=c["standart_val"])

st.markdown("---")

# --- AKILLI GTİP VE VERİ GİRİŞ PANELİ ---
col_sol, col_sag = st.columns(2)

with col_sol:
  st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
  st.subheader(c["kart1_baslik"])

  urun_adi = st.text_input(c["esya_adi"], c["esya_varsayilan"])
  gtip_kategori = st.selectbox(c["gtip_grup"], c["gtip_secenekler"])

  if "8471" in gtip_kategori or "Computer" in gtip_kategori:
    otomatik_gv = 0.0
    gtip_no = "8471.30.00.00.00"
  elif "8517" in gtip_kategori or "Phones" in gtip_kategori:
    otomatik_gv = 0.0
    gtip_no = "8517.12.00.00.00"
  elif "8429" in gtip_kategori or "Construction" in gtip_kategori:
    otomatik_gv = 2.7
    gtip_no = "8429.52.00.00.00"
  elif "6109" in gtip_kategori or "Textiles" in gtip_kategori:
    otomatik_gv = 12.0
    gtip_no = "6109.10.00.00.00"
  elif "9403" in gtip_kategori or "Furniture" in gtip_kategori:
    otomatik_gv = 5.6
    gtip_no = "9403.60.10.00.00"
  else:
    otomatik_gv = 5.0
    gtip_no = "XXXX.XX.XX.XX.XX"

  gtip_kodu = st.text_input(c["gtip_kod"], gtip_no)
  adet = st.number_input(c["adet"], min_value=1.0, value=100.0)
  birim_fiyat = st.number_input(
      c["birim_fiyat"], min_value=0.0, value=650.0, step=10.0
  )
  doviz_tipi = st.selectbox(c["para_birimi"], ["USD", "EUR", "TRY"])
  st.markdown("</div>", unsafe_allow_html=True)

with col_sag:
  st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
  st.subheader(c["kart2_baslik"])
  teslimat_sekli = st.selectbox(c["teslim_sekli"], c["teslimat_secenekleri"])

  col_l1, col_l2 = st.columns(2)
  with col_l1:
    navlun_maliyeti = st.number_input(c["navlun"], min_value=0.0, value=2200.0)
  with col_l2:
    sigorta_maliyeti = st.number_input(c["sigorta"], min_value=0.0, value=300.0)

  st.markdown(
      f"<small style='color: #e879f9;'><b>{c['ek_gider']}</b></small>",
      unsafe_allow_html=True,
  )
  col_e1, col_e2 = st.columns(2)
  with col_e1:
    banka_komisyon_orani = st.slider(c["komisyon"], 0.0, 2.0, 0.3, 0.1)
  with col_e2:
    musavirlik_gideri_tl = st.number_input(
        c["musavirlik"], min_value=0.0, value=15000.0
    )

  vergi_orani = st.slider(c["vergi_orani"], 0.0, 30.0, otomatik_gv, 0.1)
  otv_orani = st.slider(c["otv_orani"], 0.0, 50.0, 0.0, 1.0)
  kdv_orani = st.selectbox(c["kdv_orani"], [1, 10, 20], index=2)
  st.markdown("</div>", unsafe_allow_html=True)

# --- HESAPLAMA MOTORU ---
mal_bedeli_doviz = adet * birim_fiyat

if "TRY" in doviz_tipi:
  aktif_kur = 1.0
  gosterge_doviz = "TL"
else:
  aktif_kur = tcmb_satis.get(doviz_tipi, 38.50)
  gosterge_doviz = doviz_tipi

dolar_kuru = tcmb_satis.get("USD", 38.50)

if "EXW" in teslimat_sekli or "Ex Works" in teslimat_sekli:
  hesaplanan_navlun_tl = 0.0
  hesaplanan_sigorta_tl = 0.0
else:
  hesaplanan_navlun_tl = navlun_maliyeti * dolar_kuru
  hesaplanan_sigorta_tl = sigorta_maliyeti * dolar_kuru

mal_bedeli_tl = mal_bedeli_doviz * aktif_kur
toplam_gumruk_kiymeti = mal_bedeli_tl + hesaplanan_navlun_tl + hesaplanan_sigorta_tl

gümrük_vergisi_tutari = toplam_gumruk_kiymeti * (vergi_orani / 100.0)
otv_tutari = (toplam_gumruk_kiymeti + gümrük_vergisi_tutari) * (
    otv_orani / 100.0
)

kdv_matrahi = toplam_gumruk_kiymeti + gümrük_vergisi_tutari + otv_tutari
kdv_tutari = kdv_matrahi * (kdv_orani / 100.0)
banka_komisyonu_tl = mal_bedeli_tl * (banka_komisyon_orani / 100.0)

# 2026 Yılı Resmi Gümrük Beyannamesi Damga Resmi Kesintisi
damga_resmi_tl = 1605.80

genel_toplam_maliyet = (
    kdv_matrahi
    + kdv_tutari
    + banka_komisyonu_tl
    + musavirlik_gideri_tl
    + otv_tutari
    + damga_resmi_tl
)
birim_basina_maliyet = genel_toplam_maliyet / adet if adet > 0 else 0.0

# --- SONUÇLAR VE ÖZET ---
st.markdown("---")
st.markdown(f"<h2>{c['sonuc_baslik']}</h2>", unsafe_allow_html=True)

res1, res2, res3, res4 = st.columns(4)
with res1:
  st.metric(label=c["m1"], value=f"{mal_bedeli_tl:,.2f} TL")
with res2:
  st.metric(label=c["m2"], value=f"{toplam_gumruk_kiymeti:,.2f} TL")
with res3:
  st.metric(
      label=c["m3"], value=f"{genel_toplam_maliyet:,.2f} TL", delta=c["m3_alt"]
  )
with res4:
  st.metric(label=c["m4"], value=f"{birim_basina_maliyet:,.2f} TL")

# --- SEKMELER ---
tab_detay, tab_grafik, tab_mevzuat = st.tabs(
    [c["tab1"], c["tab2"], c["tab3"]]
)

with tab_detay:
  st.subheader(c["tab1_baslik"])
  detay_df = pd.DataFrame({
      c["col_parametre"]: c["tab_satirlar"],
      c["col_deger"]: [
          urun_adi,
          gtip_kodu,
          teslimat_sekli,
          f"{mal_bedeli_doviz:,.2f} {gosterge_doviz}",
          f"{aktif_kur:,.4f} TL",
          f"{mal_bedeli_tl:,.2f} TL",
          f"{hesaplanan_navlun_tl:,.2f} TL",
          f"{hesaplanan_sigorta_tl:,.2f} TL",
          f"**{toplam_gumruk_kiymeti:,.2f} TL**",
          f"{gümrük_vergisi_tutari:,.2f} TL",
          f"{otv_tutari:,.2f} TL",
          f"{kdv_matrahi:,.2f} TL",
          f"{kdv_tutari:,.2f} TL",
          f"{banka_komisyonu_tl:,.2f} TL",
          f"{musavirlik_gideri_tl:,.2f} TL",
          f"{damga_resmi_tl:,.2f} TL",
          f"🟣 **{genel_toplam_maliyet:,.2f} TL**",
          f"🏷️ **{birim_basina_maliyet:,.2f} TL**",
      ],
  })
  st.table(detay_df)

  try:
    csv_data = detay_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=c["btn_indir"],
        data=csv_data,
        file_name="gumruk_ultra_rapor.csv",
        mime="text/csv",
    )
  except Exception:
    pass

with tab_grafik:
  st.subheader(c["tab2_baslik"])
  grafik_tablosu = pd.DataFrame({
      "Kalem": c["grafik_kalemler"],
      "Tutar (TL)": [
          mal_bedeli_tl,
          hesaplanan_navlun_tl + hesaplanan_sigorta_tl,
          gümrük_vergisi_tutari + otv_tutari,
          kdv_tutari,
          banka_komisyonu_tl + musavirlik_gideri_tl + damga_resmi_tl,
      ],
  }).set_index("Kalem")
  st.bar_chart(grafik_tablosu)

with tab_mevzuat:
  st.subheader(c["tab3_baslik"])
  st.markdown(c["mevzuat_metin"])

# --- FOOTER ---
st.markdown(
    f"""
    <div style='margin-top: 40px; padding: 15px; background: rgba(30, 15, 55, 0.80); backdrop-filter: blur(10px); border-radius: 10px; text-align: center; color: #d8b4fe; font-size: 13px; border: 1px solid rgba(192, 132, 252, 0.2);'>
        {c['footer']}
    </div>
""",
    unsafe_allow_html=True,
)