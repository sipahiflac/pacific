import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np


# --- Page Configuration ---
logo2_path = os.path.join(os.path.dirname(__file__), 'icons', 'logo2.png')


st.set_page_config(
    page_title="Pacific Türkiye",
    page_icon=logo2_path,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS (Valve UI Inspired) ---
st.markdown("""
<style>
    /* General Background and Text */
    .stApp {
        background-color: #1b2838; /* Valve Dark Blue/Gray */
        color: #c7d5e0;
        font-family: 'Motiva Sans', sans-serif;
    }
    
    span[data-baseweb="tag"]{
            background-color: #2a475e;
            border-color: #5385bc;
            }
    span[data-baseweb="tag"] span {
            max-width: none;
            }

    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #101822;
        padding: 20px;
        border-radius: 4px;
        border: 1px solid #2a475e;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricLabel"] {
        color: #66c0f4; /* Valve Light Blue */
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff;
    }
    div[data-testid="stMetricDelta"] {
        color: #a3cf06; /* Valve Green for positive */
    }

    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 200;
        letter-spacing: 1px;
        font-size: 0.6rem;
    }
    
    /* Top Posts Container */
    .post-container {
        background-color: #171a21;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #2a475e;
        margin-bottom: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        text-decoration: none !important;
    }
    
    /* Image Styling - Strict Aspect Ratio with Ghost Loading */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    .post-image-container {
        width: 100%;
        padding-top: 100%; /* 1:1 Aspect Ratio */
        position: relative;
        overflow: hidden;
        border-radius: 4px;
        background-color: #171a21;
        background-image: linear-gradient(to right, #171a21 4%, #2a475e 25%, #171a21 36%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite linear;
        text-decoration: none !important;
    }
    
    .post-image-container img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 1; /* Ensure image is above the shimmer background */
        text-decoration: none !important;
    }
    
    /* City Tag Styling */
    .city-tag {
        background-color: #101822;
        color: #66c0f4;
        padding: 1px 5px;
        border-radius: 2px;
        font-size: 0.9rem;
        font-weight: 700;
        border: 1px solid   #2a475e; 
        margin-left: -16px;
        display: inline-block;
        margin-top: 6px;


    }
    
    /* Stats Text */
    .post-stats {
        margin-top: 8px;
        font-size: 12px;
        color: #8b9bd3;
        display: flex;
        justify-content: space-between;
        text-decoration: none !important;
        border-bottom: none !important;
    }

    .post-stats span {
        text-decoration: none !important;
    }

    /* Caption Text */
    .post-caption {
        margin-top: 8px;
        font-size: 11px;
        color: #c7d5e0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.4em;
        height: 2.8em; /* 2 lines * 1.4em */
        opacity: 1;
        margin-bottom: auto; /* Push link to bottom */
        border-bottom: none !important;

    }

    /* Clickable Post Card */
    .post-card-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block;
        border-bottom: none !important; 
    }
    
    .post-card-link:hover, 
    .post-card-link:focus, 
    .post-card-link:active, 
    .post-card-link:visited {
        text-decoration: none !important;
        border-bottom: none !important;
        color: inherit !important;
    }
    
    /* Force remove underline from all children */
    .post-card-link * {
        text-decoration: none !important;
        border-bottom: none !important;
    }
    

    
    
    .post-card-link .post-container {
        transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
        position: relative;
        text-decoration: none !important;
        
    }
    
    .post-card-link:hover .post-container {
        border-color: #66c0f4;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.35);
        text-decoration: none !important;
        
    }
    
    /* Rank Badge */
    .post-rank-badge {
        position: absolute;
        top: 5px;
        right: 10px;
        background: #171a21;
        color: #5385bc;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 1px 9px;
        border-radius: 2px;
  
        z-index: 10;
    }
    
    /* Profile Label for Tüm Gönderiler */
    .post-profile-label {
        font-size: 11px;
        color: #8b9bd3;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Engagement Rate Badge */
    .post-engagement-badge {
        font-size: 11px;
        color: #a3cf06;
        margin-left: 8px;
    }

    /* Plotly Chart Backgrounds */
    .js-plotly-plot .plotly .main-svg {
        background-color: rgba(0,0,0,0) !important;
    }

    /* --- Sidebar Navigation Buttons (Notion Style) --- */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        background-color: transparent;
        color: #c7d5e0;
        border: none;
        text-align: left;
        padding-left: 15px;
        justify-content: flex-start;
        margin-bottom: -5px;
        transition: background-color 0.2s; 
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.02);
        color: #ffffff;
        border: none;
    }
    
    /* Active Button Styling (Targeting Primary Buttons) */
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 500;
    }
    
    section[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
    }


    

    section[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* Responsive Chart Height */
    @media (max-width: 768px) {
        .js-plotly-plot {
            min-height: 200px !important;
        }
    }
    @media (min-width: 769px) {
        .js-plotly-plot {
            min-height: 500px !important;
           
        }
        .js-plotly-plot .plotly .main-svg {
            height: 100% !important;
               width: 100% !important;
        }
    }

</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

def load_svg(filename):
    """Load SVG content from icons directory"""
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', filename)
        with open(icon_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<!-- Icon not found: {filename} -->"

def process_captions_for_wordcloud(df):
    """Extract and process captions to get top 10 words"""
    if 'Caption' not in df.columns:
        return {}
    
    # Turkish stop words (common words to filter out)
    turkish_stopwords = {
        'bir', 'bu', 'şu', 'o', 've', 'ile', 'için', 'gibi', 'kadar', 'daha',
        'en', 'çok', 'az', 'da', 'de', 'ki', 'mi', 'mı', 'mu', 'mü',
        'var', 'yok', 'ise', 'ise', 'ama', 'fakat', 'ancak', 'lakin',
        'ben', 'sen', 'biz', 'siz', 'onlar', 'beni', 'seni', 'bizi', 'sizi',
        'benim', 'senin', 'bizim', 'sizin', 'onların', 'bana', 'sana', 'bize', 'size',
        'ne', 'nasıl', 'niçin', 'niye', 'neden', 'hangi', 'kim', 'kime', 'kimi',
        'ile', 'için', 'gibi', 'kadar', 'daha', 'en', 'çok', 'az',
        'veya', 'ya', 'hem', 'hem', 'ne', 'ne', 'de', 'da' ,'nde'
    }
    
    # Combine all captions
    all_captions = df['Caption'].dropna().astype(str).tolist()
    all_text = ' '.join(all_captions)
    
    # Remove URLs, mentions, hashtags (optional - keep hashtags for wordcloud)
    all_text = re.sub(r'http\S+|www\.\S+', '', all_text)  # Remove URLs
    all_text = re.sub(r'@\w+', '', all_text)  # Remove mentions
    
    # Extract words (Turkish characters included)
    words = re.findall(r'\b[ğüşıöçĞÜŞİÖÇa-zA-Z]+\b', all_text.lower())
    
    # Filter stop words and short words
    filtered_words = [w for w in words if w not in turkish_stopwords and len(w) > 2]
    
    # Count word frequencies
    word_counts = Counter(filtered_words)
    
    # Get top 10 words
    top_words = dict(word_counts.most_common(10))
    
    return top_words

def create_wordcloud_image(word_freq_dict):
    """Create a WordCloud image with dark theme colors"""
    if not word_freq_dict:
        return None
    
    # Valve theme colors
    colors = ['#66c0f4', '#a3cf06', '#c7d5e0', '#8b9bd3', '#d2f0a9', '#35a69e']
    font_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Datas",
        "OpenSans-Bold.ttf"
    )
    if not os.path.exists(font_path):
        font_path = None  # fall back to default
    
    # Create color function for wordcloud
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return np.random.choice(colors)
    
    # Create WordCloud with dark theme
    wordcloud = WordCloud(
        width=2000,
        height=1000,
        background_color='#1b2838',  # Dark background matching theme
        color_func=color_func,
        max_words=30,
        relative_scaling=0.5,
        colormap=None,
        font_path=font_path,
        prefer_horizontal=0.7,
        min_font_size=30,
        max_font_size=400
    ).generate_from_frequencies(word_freq_dict)
    
    # Render via matplotlib for Streamlit
    fig, ax = plt.subplots(figsize=(12, 4), facecolor='#1b2838')
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    fig.patch.set_facecolor('#1b2838')
    plt.tight_layout(pad=0)
    
    return fig

# --- Data Loading Functions ---
@st.cache_data
def load_all_data(data_dir):
    profiles = {}
    
    if not os.path.exists(data_dir):
        st.error(f"Directory not found: {data_dir}")
        return profiles

    # Scan for *Main.csv files to identify profiles
    files = os.listdir(data_dir)
    main_files = [f for f in files if f.endswith('Main.csv')]
    
    encodings_to_try = ['utf-8', 'cp1254', 'iso-8859-9']
    
    for main_file in main_files:
        profile_name = main_file.replace('Main.csv', '')
        
        try:
            # Load Main Data
            main_path = os.path.join(data_dir, main_file)
            df = None
            
            # Try encodings for Main Data
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(main_path, sep=';', encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                st.error(f"Could not read {main_file} with supported encodings.")
                continue
            
            column_mapping = {
                'PostLink': 'Link',
                'PostTürü': 'Tür',
                'BeğeniSayısı': 'Beğeni Sayısı',
                'YorumSayısı': 'Yorum Sayısı',
                'Takipçi': 'Takipçiler',
                'Likes': 'Beğeni Sayısı',
                'Comments': 'Yorum Sayısı',
                'Category': 'Tür',
                'Date': 'Tarih',
                'Link': 'Link'
            }
            df = df.rename(columns=column_mapping)
            
            # Clean Numeric Columns
            numeric_cols = ['Beğeni Sayısı', 'Yorum Sayısı', 'Görüntülenme Sayısı', 'Takipçiler']
            for col in numeric_cols:
                if col in df.columns and df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace('.', '', regex=False)
                    df[col] = df[col].str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Parse Dates with multiple formats
            if 'Tarih' in df.columns:
                # Try parsing with dayfirst=True for DD.MM.YYYY HH:MM or DD.MM.YYYY
                df['Tarih'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce')
                
                # Derived Columns
                if 'Beğeni Sayısı' in df.columns and 'Yorum Sayısı' in df.columns:
                    df['Toplam Etkileşim'] = df['Beğeni Sayısı'] + df['Yorum Sayısı']
                
                # Turkish Day Names
                day_map = {
                    'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba', 
                    'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar'
                }
                df['Gün'] = df['Tarih'].dt.day_name().map(day_map)
                days_order = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
                df['Gün'] = pd.Categorical(df['Gün'], categories=days_order, ordered=True)
                
                # Turkish Date String
                month_map = {
                    1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
                    7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
                }
                df['Tarih_Str'] = df['Tarih'].apply(lambda x: f"{x.day} {month_map[x.month]} {x.year}" if pd.notnull(x) else "")
            
                # Derive 'Atılan Saat' from 'Tarih' since it's missing in source
                df['Atılan Saat'] = df['Tarih'].dt.hour
                
                # Hour Bins
                bins = [0, 4, 8, 12, 16, 20, 24]
                labels = ['00-04', '04-08', '08-12', '12-16', '16-20', '20-24']
                df['Saat Aralığı'] = pd.cut(df['Atılan Saat'], bins=bins, labels=labels, right=False, include_lowest=True)

            profiles[profile_name] = {
                'main': df
            }
        except Exception as e:
            st.error(f"Error loading data for {profile_name}: {e}")
                
    return profiles

# --- Main App Logic ---

def main():
    # --- Sidebar & Navigation State ---
    if 'page' not in st.session_state:
        st.session_state.page = ">Rapor"
    
    page = st.session_state.page

    # --- Dynamic Header ---
    header_config = {
        ">Rapor": {
            "title": "İl Belediye Başkanları İnstagram Raporu",
            "subtitle": "Sosyal medya performanslarının detaylı incelenmesi"
        },
        ">Tüm Gönderiler": {
            "title": "Tüm Başkanların Sosyal Medya Gönderileri",
            "subtitle": "Son bir ayda atılmış sosyal medya gönderilerini; tarihe, beğeni sayısına veya diğer metriklere göre filtreleyerek analiz edin."
        },
        ">Belediye Başkanları": {
            "title": "Başkan Sosyal Medya Performans Karşılaştırması",
            "subtitle": "Beğeni sayısı, etkileşim ve içerik etkisini karşılaştırmalı olarak inceleyin."
        },
        ">YZ Aksiyonları": {
            "title": "Yapay Zeka Destekli İçgörüler",
            "subtitle": "Veri analitiği ile elde edilen stratejik öneriler ve tespitler."
        }
        
    }

    current_header = header_config.get(page, header_config[">Rapor"])
    
    st.subheader(current_header["title"])
    st.markdown(f'<p style="color: #8b9bd3; font-size: 0.9rem; margin-top: -10px;">{current_header["subtitle"]}</p>', unsafe_allow_html=True)
    st.markdown("---")

    data_dir = os.path.join(os.path.dirname(__file__), 'Datas')
    profiles = load_all_data(data_dir)

    if not profiles:
        st.warning("No profile data found in Datas directory.")
        return

    # --- Calculate Global Medians for Access Score ---
    all_followers_list = []
    all_interactions_profile_list = []
    
    for p_data in profiles.values():
        df_temp = p_data['main']
        f = df_temp['Takipçiler'].iloc[0] if 'Takipçiler' in df_temp.columns and not df_temp['Takipçiler'].isna().all() else 0
        i = df_temp['Toplam Etkileşim'].sum() if 'Toplam Etkileşim' in df_temp.columns else 0
        all_followers_list.append(f if pd.notnull(f) else 0)
        all_interactions_profile_list.append(i if pd.notnull(i) else 0)
    
    median_followers = pd.Series(all_followers_list).median() if all_followers_list else 1
    if not median_followers or median_followers == 0:
        median_followers = 1
    
    median_interactions_profile = pd.Series(all_interactions_profile_list).median() if all_interactions_profile_list else 1
    if not median_interactions_profile or median_interactions_profile == 0:
        median_interactions_profile = 1
    
    # --- Load Tags ---
    tags_path = os.path.join(data_dir, "profile_tags.csv")
    tags_df = pd.DataFrame()
    if os.path.exists(tags_path):
        try:
            tags_df = pd.read_csv(tags_path, sep=';')
            # Strip whitespace from column names and values
            tags_df.columns = tags_df.columns.str.strip()
            for col in tags_df.columns:
                if tags_df[col].dtype == 'object':
                    tags_df[col] = tags_df[col].str.strip()
        except Exception as e:
            st.error(f"Error loading profile_tags.csv: {e}")

    # --- Sidebar ---

    

    st.sidebar.image("./icons/logo.png", width=100)

    # Custom Navigation Buttons
    nav_options = [">Rapor", ">Tüm Gönderiler", ">Belediye Başkanları", ">YZ Aksiyonları"]
    
    st.sidebar.markdown("""
    <style>
        div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            align-items: center;
        }
        div[data-testid="column"] {
            padding: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    for option in nav_options:
        is_active = (st.session_state.page == option)
        btn_type = "primary" if is_active else "secondary"
        
        if st.sidebar.button(option, key=f"nav_{option}", type=btn_type, use_container_width=True):
            st.session_state.page = option
            st.rerun()
    
    st.sidebar.markdown("---")
    
    profile_names = list(profiles.keys())
    
    # Default to first profile if available
    selected_profile_name = st.sidebar.selectbox("Profil Seç", options=profile_names)
    
    compare_mode = False
    comparison_profile_name = None
    
    # Tag Filters (Only for "Tüm Gönderiler")
    selected_tags1 = []
    selected_tags2 = []
    
    if page == ">Rapor":
        compare_mode = st.sidebar.checkbox("Karşılaştırma Modu")
        if compare_mode:
            comparison_profile_name = st.sidebar.selectbox(
                "Karşılaştırılacak Profil", 
                options=[p for p in profile_names if p != selected_profile_name]
            )

    # --- Calculate Global Averages for Tooltips ---
    all_followers = []
    all_interactions = []
    all_post_counts = []
    all_avg_interactions = []

    for p_name, p_data in profiles.items():
        df_temp = p_data['main']
        
        # Followers
        f_count = df_temp['Takipçiler'].iloc[0] if 'Takipçiler' in df_temp.columns and not df_temp['Takipçiler'].isna().all() else 0
        all_followers.append(f_count)
        
        # Interactions
        i_sum = df_temp['Toplam Etkileşim'].sum() if 'Toplam Etkileşim' in df_temp.columns else 0
        all_interactions.append(i_sum)
        
        # Post Count
        p_count = len(df_temp)
        all_post_counts.append(p_count)
        
        # Avg Interaction
        avg_i = i_sum / p_count if p_count > 0 else 0
        all_avg_interactions.append(avg_i)

    global_avg_followers = sum(all_followers) / len(all_followers) if all_followers else 0
    global_avg_interaction = sum(all_interactions) / len(all_interactions) if all_interactions else 0
    global_avg_posts = sum(all_post_counts) / len(all_post_counts) if all_post_counts else 0
    global_avg_avg_interaction = sum(all_avg_interactions) / len(all_avg_interactions) if all_avg_interactions else 0

    # --- Main Content ---
    if page == ">Rapor":
        if selected_profile_name:
            selected_data = profiles[selected_profile_name]
            df = selected_data['main']

            # --- Header Info ---
            
            city_tag_html = ""
            if not tags_df.empty:
                p_tags = tags_df[tags_df['Profil'] == selected_profile_name]
                if not p_tags.empty:
                     # Check Tag3 (City)
                     if 'Tag3' in p_tags.columns and pd.notnull(p_tags.iloc[0]['Tag3']):
                         city_name = p_tags.iloc[0]['Tag3']
                         city_tag_html = f'<span class="city-tag">{city_name}</span>'
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; padding: 0; color: white; font-weight: 300; font-size: 1.8rem;">{selected_profile_name}</h3>
                {city_tag_html}
            </div>
            """, unsafe_allow_html=True)
            
            # Date Range
            if not df.empty:
                min_date = df['Tarih'].min()
                max_date = df['Tarih'].max()
                month_map = {
                    1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
                    7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
                }
                date_range_str = f"({min_date.day} {month_map[min_date.month]} – {max_date.day} {month_map[max_date.month]} {max_date.year})"
                st.caption(f"📅 {date_range_str}")

            # --- 1. KPI Metrics (Custom HTML with Hover) ---
            
            # Current Metrics
            current_followers = df['Takipçiler'].iloc[0] if 'Takipçiler' in df.columns and not df['Takipçiler'].isna().all() else 0
            follower_change = current_followers * 0.05 # Mock Delta
            
            current_posts = len(df)
            posts_delta = 5 # Fixed number
            
            current_interaction = df['Toplam Etkileşim'].sum()
            interaction_delta = current_interaction * 0.05 # Mock 5% increase
            
            avg_interaction = current_interaction / current_posts if current_posts > 0 else 0
            avg_interaction_delta = avg_interaction * 0.05 # Mock 5% increase

            # Custom CSS for Metrics
            st.markdown("""
            <style>
                .metric-card {
                    background-color: #101822;
                    padding: 15px;
                    border-radius: 4px;
                    border: 1px solid #2a475e;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                    text-align: center;
                    height: 100%;
                    transition: transform 0.2s;
                }
                .metric-card:hover {
                    transform: translateY(-1px);
                    border-color: #66c0f4;
                }
                .metric-label {
                    color: #66c0f4;
                    font-weight: bold;
                    font-size: 0.9rem;
                    margin-bottom: 5px;
                }
                .metric-sublabel {
                    color: #8b9bd3;
                    font-size: 0.7rem;
                    margin-bottom: 5px;
                }
                .metric-value {
                    color: #ffffff;
                    font-size: 1.5rem;
                    font-weight: bold;
                }
                .metric-delta {
                    font-size: 0.9rem;
                    font-weight: bold;
                }
                .delta-pos { color: #a3cf06; }
                .delta-neg { color: #ff4949; }
            </style>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            
            def metric_html(label, sublabel, value, delta, current_val, avg_val):
                delta_color = "delta-pos" if delta >= 0 else "delta-neg"
                delta_sign = "+" if delta >= 0 else ""
                sublabel_html = f'<div class="metric-sublabel">{sublabel}</div>' if sublabel else ''
                
                return f"""
                <div class="metric-card">
                <div class="metric-label">{label}</div>
                {sublabel_html}
                <div class="metric-value">{value}</div>
                <div class="metric-delta {delta_color}">{delta_sign}{delta}</div>
                </div>
                """

            with col1:
                st.markdown(metric_html("Takipçi Sayısı", "21 Kasım itibarıyla", f"{int(current_followers):,}", int(follower_change), current_followers, global_avg_followers), unsafe_allow_html=True)
            with col2:
                st.markdown(metric_html("Toplam Etkileşim", "Son 30 gündeki", f"{int(current_interaction):,}", int(interaction_delta), current_interaction, global_avg_interaction), unsafe_allow_html=True)
            with col3:
                st.markdown(metric_html("Toplam Gönderi", "Son 30 gündeki", f"{current_posts}", int(posts_delta), current_posts, global_avg_posts), unsafe_allow_html=True)
            with col4:
                st.markdown(metric_html("Ortalama Etkileşim", "Son 30 gündeki", f"{int(avg_interaction):,}", int(avg_interaction_delta), avg_interaction, global_avg_avg_interaction), unsafe_allow_html=True)

            st.markdown("---")

            # --- 2. Top Performing Posts ---
            st.subheader("En İyi Performans Gösteren Gönderiler")
            
            # Get top 4 posts
            top_posts = df.sort_values(by='Toplam Etkileşim', ascending=False).head(4)
            
            # Use 4 columns to fit in the same area (horizontally)
            cols = st.columns(4)
            
            for i, (index, row) in enumerate(top_posts.iterrows()):
                col = cols[i]
                
                # Use DisplayPhoto if available, else placeholder
                if 'DisplayPhoto' in row and pd.notnull(row['DisplayPhoto']):
                    display_src = row['DisplayPhoto']
                else:
                    display_src = "https://via.placeholder.com/400x400.png?text=No+Image"
                
                # Caption
                caption_text = row['Caption'] if 'Caption' in row and pd.notnull(row['Caption']) else "Açıklama yok."
                
                # Link
                post_link = row['Link'] if 'Link' in row and pd.notnull(row['Link']) else "#"
                
                with col:
                    st.markdown(f"""
                    <a href="{post_link}" target="_blank" class="post-card-link">
                        <div class="post-container" data-profile="{selected_profile_name}">
                            <div class="post-image-container">
                                <img src="{display_src}" alt="Top Post" loading="lazy">
                            </div>
                            <div class="post-stats">
                                <span>❤️ {int(row['Beğeni Sayısı'])}</span>
                                <span>💬 {int(row['Yorum Sayısı'])}</span>
                            </div>
                            <div class="post-caption">
                                {caption_text}
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # --- 3. Charts & Visualizations (Tabbed Interface) ---
            
            # Create two main columns for the tab groups
            col_leftmargin, chart_col, col_rightmargin = st.columns([0.25, 0.5, 0.25])
            
            # --- LEFT COLUMN TABS ---
        

            
            with chart_col:
                tab_trend, tab_format, tab_wordcloud, tab_daily, tab_hourly  = st.tabs(["Beğeni Trendi", "Format Analizi", "Kelime Haritası", "Günlük Etkileşim", "Saatlik Etkileşim"])
                
                with tab_trend:
                    st.subheader("Beğeni Trendi")
                    
                    # Group by Day and Calculate Mean
                    df_daily = df.groupby(df['Tarih'].dt.date)['Beğeni Sayısı'].mean().reset_index()
                    df_daily['Tarih'] = pd.to_datetime(df_daily['Tarih'])
                    df_daily = df_daily.sort_values('Tarih') # Ensure sorted
                    
                    # Calculate Moving Average (3-day window)
                    df_daily['MA'] = df_daily['Beğeni Sayısı'].rolling(window=3, min_periods=1).mean()
                    
                    # Use Datetime for X-axis to fix sorting/comparison issues
                    fig_line = px.line(df_daily, x='Tarih', y='Beğeni Sayısı', markers=True, template="plotly_dark", line_shape='linear')
                    fig_line.update_xaxes(showticklabels=False)
                    fig_line.update_traces(line_color='#66c0f4', line_width=2.5, name=selected_profile_name)
                    
                    # Comparison Logic
                    if compare_mode and comparison_profile_name:
                        comp_data = profiles[comparison_profile_name]['main']
                        comp_daily = comp_data.groupby(comp_data['Tarih'].dt.date)['Beğeni Sayısı'].mean().reset_index()
                        comp_daily['Tarih'] = pd.to_datetime(comp_daily['Tarih'])
                        comp_daily = comp_daily.sort_values('Tarih') # Ensure sorted
                        
                        comp_daily['MA'] = comp_daily['Beğeni Sayısı'].rolling(window=3, min_periods=1).mean()
                        
                        fig_line.add_scatter(x=comp_daily['Tarih'], y=comp_daily['MA'], mode='lines+markers', name=comparison_profile_name, line=dict(color='#a3cf06', width=1, shape='linear'))

                    fig_line.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Tarih",
                        legend_title_text='Profil',
                        xaxis=dict(
                            tickformat="%d %b", # Format: 22 Oct
                            dtick="D1", # Daily ticks if zoomed in, or auto
                            fixedrange=True
                        ),
                        yaxis=dict(fixedrange=True),
                        autosize=True,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig_line, use_container_width=True, config={'responsive': True})

                with tab_format:
                    st.subheader("Format Analizi")
                    avg_likes_type = df.groupby('Tür')['Beğeni Sayısı'].mean().reset_index()
                    # Valve Theme Colors (Updated)
                    colors = ['#66c0f4', '#d2f0a9', '#35a69e', '#c7d5e0']
                    fig_pie = px.pie(avg_likes_type, values='Beğeni Sayısı', names='Tür', hole=0.4, template="plotly_dark", color_discrete_sequence=colors)
                    fig_pie.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        autosize=True,
                        margin=dict(l=0, r=0, t=30, b=0),
                        height=400,
                    )
                    st.plotly_chart(fig_pie, use_container_width=False, config={'responsive': False})
                    
                    # Insight
                    if not avg_likes_type.empty:
                        best_type = avg_likes_type.sort_values(by='Beğeni Sayısı', ascending=False).iloc[0]
                        #st.info(f"💡 Son 30 günde en çok etkileşimi **{best_type['Tür']}** türünde atılan gönderiler aldı.")

                with tab_wordcloud:
                    st.subheader("Kelime Haritası")

                    word_freq = process_captions_for_wordcloud(df)

                    if word_freq:
                        wordcloud_fig = create_wordcloud_image(word_freq)

                        if wordcloud_fig:
                            st.pyplot(wordcloud_fig, use_container_width=True, clear_figure=True)
                            plt.close(wordcloud_fig)
                            top_words_list = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                            words_text = " • ".join([f"{word} ({count})" for word, count in top_words_list])
                            st.info(f"Açıklamalarda en çok geçen 10 kelime: {words_text}")
                        
                            
                            
                        else:
                            st.info("WordCloud oluşturulamadı.")
                    else:
                        st.info("Caption verisi bulunamadı veya yeterli kelime bulunamadı.")

                with tab_daily:
                    st.subheader("Gün Bazlı Etkileşim")
                    avg_likes_day = df.groupby('Gün', observed=True)['Beğeni Sayısı'].mean().reset_index()
                    fig_bar_day = px.bar(avg_likes_day, x='Gün', y='Beğeni Sayısı', template="plotly_dark", color='Beğeni Sayısı', color_continuous_scale='Bluyl')
                    fig_bar_day.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(fixedrange=True),
                        yaxis=dict(fixedrange=True),
                        coloraxis_showscale=False,
                        autosize=True,
                     
                        
                    )

                    fig_bar_day.update_xaxes(
                       automargin=True
                    )
                    st.plotly_chart(fig_bar_day, use_container_width=True, config={'responsive': True})
                    
                    best_day = avg_likes_day.sort_values(by='Beğeni Sayısı', ascending=False).iloc[0]
                    
                    #st.info(f"💡 Son 30 günde en çok etkileşimi **{best_day['Gün']}** günü atılan gönderiler aldı.")

                with tab_hourly:
                    st.subheader("Saat Bazlı Etkileşim (4 Saatlik)")
                    
                    # Define bins and labels
                    all_bins = ['00-04', '04-08', '08-12', '12-16', '16-20', '20-24']
                    
                    # Ensure 'Saat Aralığı' is categorical with these exact categories
                    df['Saat Aralığı'] = pd.Categorical(df['Saat Aralığı'], categories=all_bins, ordered=True)
                    
                    # Groupby using observed=False to include empty bins
                    avg_likes_hour = df.groupby('Saat Aralığı', observed=False)['Beğeni Sayısı'].mean().reset_index()
                    
                    # Explicitly convert to string for Plotly to avoid any date inference
                    avg_likes_hour['Saat Aralığı'] = avg_likes_hour['Saat Aralığı'].astype(str)
                    
                    # Updated Color Palette
                    fig_bar_hour = px.bar(avg_likes_hour, x='Saat Aralığı', y='Beğeni Sayısı', template="plotly_dark", color='Beğeni Sayısı', color_continuous_scale='Bluyl')
                    
                    fig_bar_hour.update_xaxes(
                        scaleanchor='y',
                        scaleratio=1,
                        automargin=True
                    )

                    fig_bar_hour.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Saat Aralığı",
                        xaxis_type='category', # Force categorical axis
                        xaxis=dict(fixedrange=True),
                        yaxis=dict(fixedrange=True),
                        coloraxis_showscale=False,
                        
                        margin=dict(l=0, r=0, t=0, b=100),

                    )
                    
                    st.plotly_chart(fig_bar_hour, use_container_width=True, config={'responsive': True,})
                    
                    # Insight
                    
                    best_hour = avg_likes_hour.sort_values(by='Beğeni Sayısı', ascending=False).iloc[0]
                    #if best_hour['Beğeni Sayısı'] > 0:
                        #st.info(f"💡 Son 30 günde en çok etkileşimi **{best_hour['Saat Aralığı']}** saatleri arasında atılan gönderiler aldı.")
                
        with col_rightmargin:
            st.markdown("") 
            
            
                

     # --- All Posts Page ---
    elif page == ">Tüm Gönderiler":
        st.subheader("Tüm Gönderiler")



        # Combine all data
        all_posts = []
        for p_name, p_data in profiles.items():
            temp_df = p_data['main'].copy()
            temp_df['Profil'] = p_name
            
            # Merge Tags if available
            if not tags_df.empty:
                # Filter tags for this profile
                p_tags = tags_df[tags_df['Profil'] == p_name]
                if not p_tags.empty:
                    temp_df['Tag1'] = p_tags.iloc[0]['Tag1'] if 'Tag1' in p_tags.columns else None
                    temp_df['Tag2'] = p_tags.iloc[0]['Tag2'] if 'Tag2' in p_tags.columns else None
                else:
                    temp_df['Tag1'] = None
                    temp_df['Tag2'] = None
            else:
                temp_df['Tag1'] = None
                temp_df['Tag2'] = None
            
            # Calculate Engagement Rate (Erişim Oranı)
            follower_count = temp_df['Takipçiler'].iloc[0] if 'Takipçiler' in temp_df.columns and not temp_df['Takipçiler'].isna().all() else 0

            if follower_count > 0:
                temp_df['Takipçiler'] = follower_count # Ensure all rows have the follower count
                temp_df['Erişim Oranı'] = (temp_df['Toplam Etkileşim'] / follower_count) * 100
            else:
                temp_df['Erişim Oranı'] = 0
                
            all_posts.append(temp_df)
        
        if all_posts:
            combined_df = pd.concat(all_posts, ignore_index=True)
            

            def calculate_post_score(row):
                follower_val = row['Takipçiler'] if 'Takipçiler' in row and pd.notnull(row['Takipçiler']) else 0
                interaction_val = row['Toplam Etkileşim'] if 'Toplam Etkileşim' in row and pd.notnull(row['Toplam Etkileşim']) else 0
                
                if follower_val > 0:
                    # New Formula: (Interaction / Follower^0.5) * 100
                    score = (interaction_val / np.power(follower_val, 0.7)) * 100
                    return score
                return 0
            
            combined_df['Erişim Skoru'] = combined_df.apply(calculate_post_score, axis=1)
            
            # Apply Filters
            if selected_tags1:
                combined_df = combined_df[combined_df['Tag1'].isin(selected_tags1)]
            if selected_tags2:
                combined_df = combined_df[combined_df['Tag2'].isin(selected_tags2)]
            
            # Sort by Engagement Rate
            combined_df = combined_df.sort_values(by='Erişim Oranı', ascending=False)
            
            # --- Top 8 Engagement Posts Cards ---
            st.subheader("En Yüksek Erişim Oranına Sahip Gönderiler")
            
            top_engagement_posts = combined_df.dropna(subset=['Toplam Etkileşim']).head(8)
            
            if not top_engagement_posts.empty:
                # First row of 4
                cols_row1 = st.columns(4)
                for i, (index, row) in enumerate(top_engagement_posts.head(4).iterrows()):
                    col = cols_row1[i]
                    rank = i + 1
                    
                    # DisplayPhoto
                    if 'DisplayPhoto' in row and pd.notnull(row['DisplayPhoto']):
                        display_src = row['DisplayPhoto']
                    else:
                        display_src = "https://via.placeholder.com/400x400.png?text=No+Image"
                    
                    # Caption
                    caption_text = row['Caption'] if 'Caption' in row and pd.notnull(row['Caption']) else "Açıklama yok."
                    
                    # Profile name
                    profile_name = row['Profil'] if 'Profil' in row and pd.notnull(row['Profil']) else ""
                    
                    # Engagement rate
                    engagement_rate = row['Erişim Oranı'] if 'Erişim Oranı' in row and pd.notnull(row['Erişim Oranı']) else 0
                    
                    # Link
                    post_link = row['Link'] if 'Link' in row and pd.notnull(row['Link']) else "#"
                    
                    with col:
                        st.markdown(f"""
                        <a href="{post_link}" target="_blank" class="post-card-link">
                            <div class="post-container">
                                <div class="post-rank-badge">{rank}</div>
                                <div class="post-profile-label">{profile_name}</div>
                                <div class="post-image-container">
                                    <img src="{display_src}" alt="Top Post">
                                </div>
                                <div class="post-stats">
                                    <span>❤️ {int(row['Beğeni Sayısı'])}</span>
                                    <span>💬 {int(row['Yorum Sayısı'])}</span>
                                    <span class="post-engagement-badge">📈 {engagement_rate:.2f}%</span>
                                </div>
                                <div class="post-caption">
                                    {caption_text}
                                </div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)
                
                # Second row of 4 (if we have more than 4 posts)
                if len(top_engagement_posts) > 4:
                    cols_row2 = st.columns(4)
                    for i, (index, row) in enumerate(top_engagement_posts.iloc[4:8].iterrows()):
                        col = cols_row2[i]
                        rank = i + 5
                        
                        # DisplayPhoto
                        if 'DisplayPhoto' in row and pd.notnull(row['DisplayPhoto']):
                            display_src = row['DisplayPhoto']
                        else:
                            display_src = "https://via.placeholder.com/400x400.png?text=No+Image"
                        
                        # Caption
                        caption_text = row['Caption'] if 'Caption' in row and pd.notnull(row['Caption']) else "Açıklama yok."
                        
                        # Profile name
                        profile_name = row['Profil'] if 'Profil' in row and pd.notnull(row['Profil']) else ""
                        
                        # Engagement rate
                        engagement_rate = row['Erişim Oranı'] if 'Erişim Oranı' in row and pd.notnull(row['Erişim Oranı']) else 0
                        
                        # Link
                        post_link = row['Link'] if 'Link' in row and pd.notnull(row['Link']) else "#"
                        
                        with col:
                            st.markdown(f"""
                            <a href="{post_link}" target="_blank" class="post-card-link">
                                <div class="post-container">
                                    <div class="post-rank-badge">{rank}</div>
                                    <div class="post-profile-label">{profile_name}</div>
                                    <div class="post-image-container">
                                        <img src="{display_src}" alt="Top Post">
                                    </div>
                                    <div class="post-stats">
                                        <span>❤️ {int(row['Beğeni Sayısı'])}</span>
                                        <span>💬 {int(row['Yorum Sayısı'])}</span>
                                        <span class="post-engagement-badge">📈 {engagement_rate:.2f}%</span>
                                    </div>
                                    <div class="post-caption">
                                        {caption_text}
                                    </div>
                                </div>
                            </a>
                            """, unsafe_allow_html=True)
            else:
                st.info("Seçilen filtrelere göre gösterilecek gönderi bulunamadı.")
            
            st.markdown("---")
            if not tags_df.empty:
                col_filter1 = st.container()
                with col_filter1:
                    unique_tags1 = sorted(tags_df['Tag1'].dropna().unique().tolist()) if 'Tag1' in tags_df.columns else []
                    selected_tags1 = st.multiselect("Bölgeler", options=unique_tags1, default=unique_tags1, key="filter_region_posts")
            else:
                selected_tags1 = []
            # Display Table
            # Removed 'Kategori'
            display_cols = ['Profil', 'Tag1', 'Tag2', 'Tarih', 'Tür', 'Beğeni Sayısı', 'Yorum Sayısı', 'Görüntülenme Sayısı', 'Erişim Oranı', 'Erişim Skoru', 'Link']
            
            # Filter columns that actually exist in the dataframe (to prevent errors if some columns are missing in old data)
            valid_cols = [col for col in display_cols if col in combined_df.columns]
            display_df = combined_df[valid_cols]
            
            # Apply Styling
            
            def highlight_selected(row):
                if row['Profil'] == selected_profile_name:
                    return ['background-color: rgba(102, 192, 244, 0.1)'] * len(row)
                return [''] * len(row)
            
            # Muted/Dark Theme Friendly Region Colors
            region_colors = {
                'İç Anadolu': '#435585', # Muted Green
                'Karadeniz': '#4A6F8A', # Muted Blue
                'Marmara': '#8A5A5A', # Muted Red/Brown
                'Ege': '#512B81', # Tealish
                'Akdeniz': '#8A8A5A', # Olive
                'Güneydoğu Anadolu': '#8A6F4A', # Earthy
                'Doğu Anadolu': '#6F4A8A', # Muted Purple
                'Büyükşehir': '#1a1c24', # Dark Gray
                'Büyükşehir Olmayan': '#1a1c24' # Slightly Lighter Gray
            }

            def style_tag1(v):
                color = region_colors.get(v, '#2a475e')
                return f'background-color: {color}; color: #e0e0e0; border-radius: 4px; padding: 2px;' if pd.notnull(v) else ''
            
            def style_tag2(v):
                color = region_colors.get(v, '#2a475e')
                return f'background-color: {color}; color: #e0e0e0; border-radius: 4px; padding: 2px;' if pd.notnull(v) else ''

            styled_df = display_df.head(st.session_state.get('post_limit', 50)).style.apply(highlight_selected, axis=1)
            styled_df = styled_df.map(style_tag1, subset=['Tag1']).map(style_tag2, subset=['Tag2'])

            st.dataframe(
                styled_df,
                column_config={
                    "Profil": st.column_config.TextColumn("Profil", pinned=True),
                    "Link": st.column_config.LinkColumn("Link"),
                    "Tarih": st.column_config.DateColumn("Tarih", format="DD.MM.YYYY"),
                    "Erişim Oranı": st.column_config.NumberColumn("Erişim Oranı", format="%.2f %%"),
                    "Erişim Skoru": st.column_config.NumberColumn("Erişim Skoru", format="%.2f", help="(Toplam Etkileşim / Takipçi^0.5) * 100"),
                    "Tag1": st.column_config.TextColumn("Bölge"),
                    "Tag2": st.column_config.TextColumn("Statü"),
                    "Görüntülenme Sayısı": st.column_config.NumberColumn("Görüntülenme", format="%d"),
                    "Beğeni Sayısı": st.column_config.NumberColumn("Beğeni Sayısı", format="%d"),
                    "Yorum Sayısı": st.column_config.NumberColumn("Yorum Sayısı", format="%d"),
                     
                },
                use_container_width=True,
                hide_index=True,
                height=500
    
            )
            
            st.caption("**Erişim Oranı**: (Toplam Etkileşim / Takipçi Sayısı) * 100 formülü ile hesaplanmıştır.")
            st.caption("**Toplam Etkileşim / (Takipçi Sayısı^{0.7}) formülü 100 ile ölçeklenerek hesaplanmıştır.**")
            
            # Limit Selection (Bottom Left)
            col_limit, col_empty = st.columns([1, 4])
            with col_limit:
                st.number_input("Gösterilecek Gönderi Sayısı", min_value=1, max_value=1000, value=50, step=10, key='post_limit')

    # --- All Mayors Page ---
    elif page == ">Belediye Başkanları":
        st.subheader("Tüm Belediye Başkanları Performans Özeti")

        # Filtre Alanı
        if not tags_df.empty:
            col_filter1 = st.container()
            with col_filter1:
                unique_tags1 = sorted(tags_df['Tag1'].dropna().unique().tolist()) if 'Tag1' in tags_df.columns else []
                selected_tags1 = st.multiselect("Bölgeler", options=unique_tags1, default=unique_tags1, key="filter_region_mayors", )

        else:
            selected_tags1 = []

        
        summary_data = []
        for p_name, p_data in profiles.items():
            df = p_data['main']
            
            current_posts = len(df)
            current_interaction = df['Toplam Etkileşim'].sum()
            avg_interaction = current_interaction / current_posts if current_posts > 0 else 0
            
            # Calculate Average Engagement Rate
            follower_count = df['Takipçiler'].iloc[0] if 'Takipçiler' in df.columns and not df['Takipçiler'].isna().all() else 0
            
            if follower_count > 0:
                # Calculate per post then average
                df['Erişim Oranı'] = (df['Toplam Etkileşim'] / follower_count) * 100
                avg_engagement_rate = df['Erişim Oranı'].mean()
            else:
                avg_engagement_rate = 0
            
            # Get Likes History (last 30 days or all available)
            # Ensure chronological order for the chart
            df_sorted = df.sort_values(by='Tarih', ascending=True)
            likes_history = df_sorted['Beğeni Sayısı'].fillna(0).tolist()

            # Tags
            tag1 = None
            tag2 = None
            if not tags_df.empty:
                p_tags = tags_df[tags_df['Profil'] == p_name]
                if not p_tags.empty:
                    tag1 = p_tags.iloc[0]['Tag1'] if 'Tag1' in p_tags.columns else None
                    tag2 = p_tags.iloc[0]['Tag2'] if 'Tag2' in p_tags.columns else None
            
            # Access Score (profile level)
            if follower_count > 0:
                access_score = (current_interaction / np.power(follower_count, 0.5))
            else:
                access_score = 0 
            summary_data.append({
                'Profil': p_name,
                'Tag1': tag1,
                'Tag2': tag2,
                'Takipçi Sayısı': follower_count,
                'Toplam Gönderi': current_posts,
                'Toplam Etkileşim': current_interaction,
                'Ortalama Etkileşim': avg_interaction,
                'Ortalama Erişim Oranı': avg_engagement_rate,
                'Erişim Skoru': access_score ,
                'views_history': likes_history
            })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)

            # Apply Filters
            if selected_tags1:
                summary_df = summary_df[summary_df['Tag1'].isin(selected_tags1)]
            if selected_tags2:
                summary_df = summary_df[summary_df['Tag2'].isin(selected_tags2)]
            
            # Sort by Total Interaction by default
            summary_df = summary_df.sort_values(by='Toplam Etkileşim', ascending=False)
            
            st.dataframe(
                summary_df,
                column_config={
                    "Profil": st.column_config.TextColumn("Profil", pinned=True),
                    "Tag1": st.column_config.TextColumn("Bölge"),
                    "Tag2": st.column_config.TextColumn("Statü"),
                    "Takipçi Sayısı": st.column_config.NumberColumn("Takipçi Sayısı", format="%d"),
                    "Toplam Gönderi": st.column_config.NumberColumn("Toplam Gönderi", format="%d"),
                    "Toplam Etkileşim": st.column_config.NumberColumn("Toplam Etkileşim", format="%d"),
                    "Ortalama Etkileşim": st.column_config.NumberColumn("Ortalama Etkileşim", format="%d"),
                    "Ortalama Erişim Oranı": st.column_config.NumberColumn("Ortalama Erişim Oranı", format="%.2f %%"),
                    "Erişim Skoru": st.column_config.NumberColumn("Erişim Skoru", format="%.2f", help="(Toplam Etkileşim / Takipçi Sayısı}^(1/2))"),
                    "views_history": st.column_config.LineChartColumn(
                        "Beğeni Grafiği (Son 30 Gün)", y_min=0, y_max=5000
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
            st.caption("**Erişim Skoru**: (Toplam Etkileşim / Takipçi Sayısı}^(1/2)) formülü ile hesaplanmıştır.")

    # --- AI Actions Page ---
    elif page == ">YZ Aksiyonları":
        st.subheader("Stratejik İçgörüler")
        
        st.markdown("""
        <style>
            .insight-card {
                background-color: #101822;
                border: 1px solid #2a475e;
                border-radius: 8px;
                padding: 20px;
                height: 280px; /* Fixed height for uniformity */
                display: flex;
                flex-direction: column;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.2s ease, border-color 0.2s ease;
                position: relative;
                overflow: hidden;
                margin-bottom: 20px;
            }
            .insight-card:hover {
                transform: translateY(-5px);
                border-color: #66c0f4;
                box-shadow: 0 8px 15px rgba(0,0,0,0.5);
            }
            .insight-icon-container {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 48px;
                height: 48px;
                background-color: rgba(102, 192, 244, 0.1);
                border-radius: 8px;
                margin-bottom: 15px;
            }
            .insight-icon svg {
                width: 28px;
                height: 28px;
                fill: #66c0f4;
            }
            .insight-title {
                color: #66c0f4;
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 10px;
                letter-spacing: 0.5px;
            }
            .insight-text {
                color: #c7d5e0;
                font-size: 0.95rem;
                line-height: 1.5;
                font-weight: 400;
                flex-grow: 1; /* Push content to fill space */
            }
            .highlight {
                color: #a3cf06;
                font-weight: bold;
            }
            .highlight-neg {
                color: #ff4949;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

        # --- Calculations for Dynamic Blocks ---
        
        # 1. Etkileşim Gücü (Interaction Power)
        # Compare profile's avg interaction to global avg interaction
        if selected_profile_name and selected_profile_name in profiles:
            p_data = profiles[selected_profile_name]['main']
            current_interaction = p_data['Toplam Etkileşim'].sum() if 'Toplam Etkileşim' in p_data.columns else 0
            current_posts = len(p_data)
            avg_interaction = current_interaction / current_posts if current_posts > 0 else 0
            
            if global_avg_avg_interaction > 0:
                interaction_power_diff = ((avg_interaction - global_avg_avg_interaction) / global_avg_avg_interaction) * 100
            else:
                interaction_power_diff = 0
                
            if interaction_power_diff >= 0:
                int_power_text = f"Etkileşim Gücü ortalamadan <span class='highlight'>%{abs(interaction_power_diff):.1f} fazla</span>."
            else:
                int_power_text = f"Etkileşim Gücü ortalamadan <span class='highlight-neg'>%{abs(interaction_power_diff):.1f} az</span>."
                
            # 2. Sadık Kitle (Loyal Audience)
            # Comments / Likes ratio
            total_likes = p_data['Beğeni Sayısı'].sum() if 'Beğeni Sayısı' in p_data.columns else 0
            total_comments = p_data['Yorum Sayısı'].sum() if 'Yorum Sayısı' in p_data.columns else 0
            
            if total_likes > 0:
                loyal_ratio = (total_comments / total_likes) * 100
            else:
                loyal_ratio = 0
                
            loyal_text = f"Her yüz beğeniye karşılık <span class='highlight'>%{loyal_ratio:.1f}</span> yorum alıyorsunuz."
            
        else:
            int_power_text = "Veri yok."
            loyal_text = "Veri yok."

        # --- Define Insights Data ---
        insights = [
            {
                "title": "Altın Saat",
                "icon": "timer-line.svg",
                "text": "Sabah (06-12.00) paylaşılan gönderiler, öğle (12-18.00) saatlerinde atılanlara göre <span class='highlight'>%71 daha fazla</span> beğeni (etkileşim puanı) topluyor."
            },
            {
                "title": "Format Analizi",
                "icon": "film-line.svg",
                "text": "Reels videoların doğası gereği viral olma potansiyelinin yüksek olmasından dolayı, diğer içeriklerden <span class='highlight'>%124 daha fazla</span> beğeni alıyor."
            },
            {
                "title": "Takvim Aksiyomu",
                "icon": "calendar-line.svg",
                "text": "Hafta sonu gönderileri, hafta içine göre yaklaşık <span class='highlight'>%41.4 daha fazla</span> beğeni alıyor."
            },
            {
                "title": "İstikrar Skoru",
                "icon": "honour-line.svg",
                "text": "Her gün aynı saatte gönderi atmak veya belirli aralıklarla gönderi atmak ile takipçilere ulaşmak arasında (-0.43 korelasyon) hafif bir korelasyon var."
            },
            {
                "title": "Sadık Kitle",
                "icon": "shake-hands-line.svg",
                "text": loyal_text
            },
            {
                "title": "Etkileşim Gücü",
                "icon": "bar-chart-box-ai-line.svg",
                "text": int_power_text
            }
        ]

        # --- Render Grid (3 Columns) ---
        rows = [insights[i:i+3] for i in range(0, len(insights), 3)]
        
        for row in rows:
            cols = st.columns(3)
            for i, card in enumerate(row):
                with cols[i]:
                    svg_content = load_svg(card['icon'])
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-icon-container">
                            <div class="insight-icon">{svg_content}</div>
                        </div>
                        <div class="insight-title">{card['title']}</div>
                        <div class="insight-text">{card['text']}</div>
                    </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()