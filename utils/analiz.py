import os
import pandas as pd
import glob
import math
import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def get_all_names():
    """
    Scans the data directory for files ending with 'Main.csv'
    and extracts the names (e.g., 'Adem Uzun' from 'Adem UzunMain.csv').
    """
    files = glob.glob(os.path.join(DATA_DIR, '*Main.csv'))
    names = []
    for f in files:
        basename = os.path.basename(f)
        name = basename.replace('Main.csv', '')
        names.append(name)
    return names

def get_city_map():
    """
    Reads profile_tags.csv and returns a dictionary mapping names to cities (Tag3).
    """
    tags_path = os.path.join(DATA_DIR, 'profile_tags.csv')
    city_map = {}
    if os.path.exists(tags_path):
        try:
            # Read CSV with semicolon delimiter
            df = pd.read_csv(tags_path, sep=';')
            # Create a dictionary {Profil: Tag3}
            # Strip whitespace just in case
            for _, row in df.iterrows():
                if pd.notna(row['Profil']) and pd.notna(row['Tag3']):
                    city_map[row['Profil'].strip()] = row['Tag3'].strip()
        except Exception as e:
            print(f"Error reading profile_tags.csv: {e}")
    return city_map

def get_region_map():
    """
    Reads profile_tags.csv and returns a dictionary mapping names to regions (Tag1).
    """
    tags_path = os.path.join(DATA_DIR, 'profile_tags.csv')
    region_map = {}
    if os.path.exists(tags_path):
        try:
            # Read CSV with semicolon delimiter
            df = pd.read_csv(tags_path, sep=';')
            # Create a dictionary {Profil: Tag1}
            for _, row in df.iterrows():
                if pd.notna(row['Profil']) and pd.notna(row['Tag1']):
                    region_map[row['Profil'].strip()] = row['Tag1'].strip()
        except Exception as e:
            print(f"Error reading profile_tags.csv for regions: {e}")
    return region_map

def get_all_posts_data():
    """
    Aggregates posts from all mayors.
    Returns a list of dictionaries.
    """
    names = get_all_names()
    region_map = get_region_map()
    city_map = get_city_map()
    all_posts = []

    for name in names:
        csv_path = os.path.join(DATA_DIR, f"{name}Main.csv")
        if not os.path.exists(csv_path):
            continue

        try:
            df = pd.read_csv(csv_path, sep=';')
            
            # Ensure numeric columns
            df['BeğeniSayısı'] = pd.to_numeric(df['BeğeniSayısı'], errors='coerce').fillna(0)
            df['YorumSayısı'] = pd.to_numeric(df['YorumSayısı'], errors='coerce').fillna(0)
            df['Takipçi'] = pd.to_numeric(df['Takipçi'], errors='coerce').fillna(0)
            
            followers = df['Takipçi'].iloc[0] if not df.empty else 0
            region = region_map.get(name, "Bilinmiyor")
            city = city_map.get(name, "Bilinmiyor")

            for _, row in df.iterrows():
                likes = row['BeğeniSayısı']
                comments = row['YorumSayısı']
                total_interaction = likes + comments
                
                # Calculate Reach Rate: (Likes + Comments) / Followers * 100
                reach_rate = (total_interaction / followers * 100) if followers > 0 else 0
                
                post_link = str(row['PostLink']) if pd.notna(row['PostLink']) else ""
                
                all_posts.append({
                    "mayor": name,
                    "region": region,
                    "city": city,
                    "likes": int(likes),
                    "comments": int(comments),
                    "reach_rate": reach_rate,
                    "type": row['PostTürü'] if pd.notna(row['PostTürü']) else "Bilinmiyor",
                    "link": post_link
                })

        except Exception as e:
            print(f"Error processing posts for {name}: {e}")
            continue

    # Sort by Reach Rate descending by default
    all_posts.sort(key=lambda x: x['reach_rate'], reverse=True)
    return all_posts

def get_mayors_data():
    """
    Aggregates statistics for each mayor.
    Returns a list of dictionaries.
    """
    names = get_all_names()
    region_map = get_region_map()
    city_map = get_city_map()
    mayors_data = []

    for name in names:
        csv_path = os.path.join(DATA_DIR, f"{name}Main.csv")
        if not os.path.exists(csv_path):
            continue

        try:
            df = pd.read_csv(csv_path, sep=';')
            
            # Ensure numeric columns
            df['BeğeniSayısı'] = pd.to_numeric(df['BeğeniSayısı'], errors='coerce').fillna(0)
            df['YorumSayısı'] = pd.to_numeric(df['YorumSayısı'], errors='coerce').fillna(0)
            df['Takipçi'] = pd.to_numeric(df['Takipçi'], errors='coerce').fillna(0)
            
            total_posts = len(df)
            if total_posts == 0:
                continue

            followers = df['Takipçi'].iloc[0] if not df.empty else 0
            region = region_map.get(name, "Bilinmiyor")
            city = city_map.get(name, "Bilinmiyor")
            
            total_likes = df['BeğeniSayısı'].sum()
            total_comments = df['YorumSayısı'].sum()
            total_interaction = total_likes + total_comments
            
            avg_likes = total_likes / total_posts
            avg_comments = total_comments / total_posts
            
            # Avg Interaction per post
            avg_interaction = total_interaction / total_posts
            
            # Avg Reach Rate: (Avg Interaction / Followers) * 100
            avg_reach_rate = (avg_interaction / followers * 100) if followers > 0 else 0

            mayors_data.append({
                "mayor": name,
                "region": region,
                "city": city,
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "avg_reach_rate": avg_reach_rate
            })

        except Exception as e:
            print(f"Error processing mayor data for {name}: {e}")
            continue
    
    # Sort by Avg Reach Rate descending by default
    mayors_data.sort(key=lambda x: x['avg_reach_rate'], reverse=True)
    return mayors_data

def analyze_data(name):
    """
    Reads the CSV for the given name and calculates KPIs and Top Posts.
    """
    csv_path = os.path.join(DATA_DIR, f"{name}Main.csv")
    
    if not os.path.exists(csv_path):
        return None

    try:
        # Read CSV with semicolon delimiter
        df = pd.read_csv(csv_path, sep=';')
        
        # Ensure numeric columns are actually numeric
        df['BeğeniSayısı'] = pd.to_numeric(df['BeğeniSayısı'], errors='coerce').fillna(0)
        df['YorumSayısı'] = pd.to_numeric(df['YorumSayısı'], errors='coerce').fillna(0)
        df['Takipçi'] = pd.to_numeric(df['Takipçi'], errors='coerce').fillna(0)

        # Get City
        city_map = get_city_map()
        city = city_map.get(name, "Bilinmiyor")

        # --- KPI Calculations ---
        
        # 1. Total Posts
        total_posts = len(df)
        
        # 2. Followers (Take from the first row, assuming it's consistent or latest)
        followers = df['Takipçi'].iloc[0] if not df.empty else 0
        
        # 3. Total Interaction (Likes + Comments)
        df['TotalInteraction'] = df['BeğeniSayısı'] + df['YorumSayısı']
        total_interaction = df['TotalInteraction'].sum()
        
        # 4. Avg Interaction (Total Interaction / Total Posts)
        avg_interaction = total_interaction / total_posts if total_posts > 0 else 0
        
        # 5. Avg Reach Rate (Avg Interaction / Followers)
        # Note: User formula: Ortalama Erişim Oranı = Ortalama Etkileşim / Takipçi Sayısı
        avg_reach_rate = (avg_interaction / followers) * 100 if followers > 0 else 0

        # Formatting for UI
        kpi_data = {
            "followers": {
                "title": "Takipçi Sayısı",
                "value": f"{int(followers):,}".replace(",", "."),
                "trend": "+12.03%", # Placeholder
                "trend_direction": "up",
                "icon": "MingcuteStarFill.svg"
            },
            "interaction": {
                "title": "Ort. Etkileşim Sayısı",
                "value": f"{int(avg_interaction):,}".replace(",", "."),
                "trend": "+5.2%", # Placeholder
                "trend_direction": "up",
                "icon": "MingcuteThumbUp2Fill.svg"
            },
            "reach": {
                "title": "Ort. Erişim Oranı",
                "value": f"%{avg_reach_rate:.2f}",
                "trend": "-1.5%", # Placeholder
                "trend_direction": "down",
                "icon": "MingcuteUser2Fill.svg"
            },
            "posts": {
                "title": "Toplam Gönderi Sayısı",
                "value": str(total_posts),
                "trend": "0",
                "trend_direction": "up",
                "icon": "MingcutePhotoAlbumFill.svg"
            }
        }

        # --- Top Posts ---
        # Sort by Total Interaction descending and take top 4
        top_posts_df = df.sort_values(by='TotalInteraction', ascending=False).head(4)
        
        top_posts = []
        for _, row in top_posts_df.iterrows():
            # Handle nan caption
            caption = row['Caption']
            if pd.isna(caption) or str(caption).lower() == 'nan':
                caption = ""
            
            # Clean the link (remove query params) and ensure trailing slash
            post_link = row['PostLink']
            if pd.notna(post_link):
                post_link = str(post_link)
                if '?' in post_link:
                    post_link = post_link.split('?')[0]
                if not post_link.endswith('/'):
                    post_link += '/'
                
                try:
                    response = requests.get(post_link, timeout=10)
                    soup = BeautifulSoup(response.content, "html.parser")
                    meta_tag = soup.find("meta", property="og:image")
                    if meta_tag:
                        image_url = meta_tag["content"]
                    else:
                        image_url = ""
                except Exception as e:
                    print(f"Error fetching image for {post_link}: {e}")
                    image_url = ""
            else:
                image_url = ""

            top_posts.append({
                "image": image_url,
                "caption": caption,
                "likes": int(row['BeğeniSayısı']),
                "comments": int(row['YorumSayısı']),
                "date": row['Tarih'],
                "link": row['PostLink']
            })

        return {
            "kpi_data": kpi_data,
            "top_posts": top_posts,
            "city": city,
            "chart_data": prepare_chart_data(df)
        }

    except Exception as e:
        print(f"Error analyzing data for {name}: {e}")
        return None

def prepare_chart_data(df):
    """
    Calculates data for the 4 requested charts.
    """
    try:
        # Convert Date to datetime
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
        
        # --- Chart A: Daily Trend (Area Chart) ---
        # Group by Date (YYYY-MM-DD) and calc Mean Likes
        daily_likes = df.groupby(df['Tarih'].dt.date)['BeğeniSayısı'].mean()
        # Sort by date
        daily_likes = daily_likes.sort_index()
        
        # Format Date as "7 Kasım"
        month_map = {
            1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
            7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
        }
        
        def format_date_tr(d):
            return f"{d.day} {month_map[d.month]}"

        chart_a = {
            "labels": [format_date_tr(d) for d in daily_likes.index],
            "values": [int(round(v)) for v in daily_likes.values]
        }

        # --- Chart B: Post Type Distribution (Polar Area) ---
        # Group by PostTürü and calc Mean Likes
        type_likes = df.groupby('PostTürü')['BeğeniSayısı'].mean()
        chart_b = {
            "labels": type_likes.index.tolist(),
            "values": [int(round(v)) for v in type_likes.values]
        }

        # --- Chart C: Hourly Analysis (Bar Chart) ---
        # Extract Hour, bin into 4-hour intervals
        # 0-4, 4-8, 8-12, 12-16, 16-20, 20-24
        bins = [0, 4, 8, 12, 16, 20, 24]
        labels = ['00-04:00', '04-08:00', '08-12:00', '12-16:00', '16-20:00', '20-24:00']
        df['Hour'] = df['Tarih'].dt.hour
        df['HourBin'] = pd.cut(df['Hour'], bins=bins, labels=labels, right=False)
        hourly_likes = df.groupby('HourBin')['BeğeniSayısı'].mean().fillna(0)
        chart_c = {
            "labels": labels,
            "values": [int(round(hourly_likes.get(l, 0))) for l in labels]
        }

        # --- Chart D: Day of Week Analysis (Bar Chart) ---
        # Day names (Monday=0, Sunday=6)
        days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        df['DayOfWeek'] = df['Tarih'].dt.dayofweek
        day_likes = df.groupby('DayOfWeek')['BeğeniSayısı'].mean()
        # Ensure all days are present
        chart_d = {
            "labels": days,
            "values": [int(round(day_likes.get(i, 0))) for i in range(7)]
        }

        return {
            "chart_a": chart_a,
            "chart_b": chart_b,
            "chart_c": chart_c,
            "chart_d": chart_d
        }

    except Exception as e:
        print(f"Error preparing chart data: {e}")
        return {}
