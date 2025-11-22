import streamlit as st
import requests

# -----------------------------------------------------------
# 1. ページ設定 & 視認性重視のCSS
# -----------------------------------------------------------
st.set_page_config(page_title="LOL.GG", page_icon="⚔️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');

    /* === 全体のテーマ === */
    .stApp {
        background-color: #0f0f0f;
        color: #e0e0e0;
        font-family: 'Roboto', sans-serif;
    }
    
    /* === タイトルロゴ === */
    h1 {
        font-family: 'Bebas Neue', sans-serif;
        color: #c8aa6e;
        font-size: 4rem !important;
        text-shadow: 0px 0px 20px rgba(200, 170, 110, 0.4);
        text-align: center;
        margin-top: -20px;
    }

    /* === ★修正点: 検索ボックスエリアを強調 === */
    .search-panel {
        background-color: #1e1e1e; /* 少し明るい黒 */
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #444;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }

    /* === 入力欄のラベル (自分/相手) === */
    .stSelectbox > label {
        color: #c8aa6e !important; /* ゴールドにして目立たせる */
        font-size: 1.2rem !important;
        font-weight: bold !important;
        margin-bottom: 8px;
    }

    /* === 入力ボックス本体 === */
    div[data-baseweb="select"] > div {
        background-color: #333 !important;
        border-color: #666 !important;
        color: white !important;
        font-size: 1.1rem !important; /* 文字サイズアップ */
    }
    
    /* === ヒーローセクション (壁紙) === */
    .hero-container {
        position: relative;
        width: 100%;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
        border: 1px solid #333;
        overflow: hidden;
    }
    .hero-image {
        width: 100%;
        display: block;
        mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 50%, rgba(0,0,0,0) 100%);
        -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 50%, rgba(0,0,0,0) 100%);
    }
    .hero-overlay {
        position: absolute;
        bottom: 30px;
        left: 40px;
        text-shadow: 2px 2px 10px #000;
    }
    .hero-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 5rem;
        color: #fff;
        line-height: 1;
    }
    
    /* === スキルカード === */
    .skill-card {
        background-color: #1a1a1a;
        border-radius: 8px;
        border: 1px solid #444;
        padding: 0;
        transition: transform 0.2s;
        margin-bottom: 10px;
    }
    .skill-card:hover {
        transform: translateY(-5px);
        border-color: #c8aa6e;
    }
    .skill-img { width: 100%; border-radius: 8px 8px 0 0; opacity: 0.9; }
    .skill-info { padding: 10px; text-align: center; }
    .skill-key { color: #c8aa6e; font-weight: bold; font-size: 0.9rem; }
    .skill-cd { color: white; font-weight: bold; font-size: 1.2rem; }

    /* === ボタン === */
    div.stButton > button {
        background-color: #333;
        color: white;
        border: 1px solid #555;
        font-weight: bold;
        height: 3em;
    }
    div.stButton > button:hover {
        border-color: #c8aa6e;
        color: #c8aa6e;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------
# 2. データ取得
# -----------------------------------------------------------
@st.cache_data
def load_data():
    try:
        v_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        version = requests.get(v_url).json()[0]
        c_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ja_JP/champion.json"
        data = requests.get(c_url).json()['data']
        champ_list = []
        id_map = {} 
        for key, val in data.items():
            display_name = f"{val['name']} ({key})" 
            champ_list.append(display_name)
            id_map[display_name] = key
        return version, sorted(champ_list), id_map
    except:
        return None, [], {}

# -----------------------------------------------------------
# 3. メイン処理
# -----------------------------------------------------------
def main():
    st.markdown("<h1>LOL.GG</h1>", unsafe_allow_html=True)

    version, champ_list, id_map = load_data()
    if not version: return

    # === 検索パネル (枠で囲って強調) ===
    with st.container():
        st.markdown('<div class="search-panel">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🔵 Your Pick")
            my_choice = st.selectbox("自分", champ_list, index=None, label_visibility="collapsed", placeholder="自分のキャラを選択...")
        with c2:
            st.markdown("#### 🔴 Enemy Pick")
            enemy_choice = st.selectbox("相手", champ_list, index=None, label_visibility="collapsed", placeholder="相手のキャラを選択...")
        st.markdown('</div>', unsafe_allow_html=True)

    # === データ表示 ===
    if my_choice and enemy_choice:
        enemy_id = id_map[enemy_choice]
        enemy_name_jp = enemy_choice.split(" (")[0]
        
        detail_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ja_JP/champion/{enemy_id}.json"
        try:
            res = requests.get(detail_url).json()['data'][enemy_id]
            spells = res['spells']
            passive = res['passive']
        except:
            st.error("Error")
            return

        # 壁紙エリア
        splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{enemy_id}_0.jpg"
        st.markdown(f"""
        <div class="hero-container">
            <img src="{splash_url}" class="hero-image">
            <div class="hero-overlay">
                <div class="hero-title">{enemy_id.upper()}</div>
                <p style="color:#ccc; font-size: 1.2rem;">VS {enemy_name_jp}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # スキルカード
        cols = st.columns(5)
        
        # Passive
        with cols[0]:
            pas_img = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/passive/{passive['image']['full']}"
            st.markdown(f"""
            <div class="skill-card">
                <img src="{pas_img}" class="skill-img">
                <div class="skill-info">
                    <div class="skill-key">Passive</div>
                    <div class="skill-cd" style="font-size:1rem;">-</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # QWER
        keys = ['Q', 'W', 'E', 'R']
        for i, spell in enumerate(spells):
            cd_text = " / ".join(map(str, spell['cooldown']))
            spell_img = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{spell['id']}.png"
            with cols[i+1]:
                st.markdown(f"""
                <div class="skill-card">
                    <img src="{spell_img}" class="skill-img">
                    <div class="skill-info">
                        <div class="skill-key">{keys[i]}</div>
                        <div class="skill-cd">{cd_text}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ボタン
        url_my = "wukong" if id_map[my_choice] == "MonkeyKing" else id_map[my_choice].lower()
        url_enemy = "wukong" if enemy_id == "MonkeyKing" else enemy_id.lower()
        
        deeplol = f"https://www.deeplol.gg/champions/{url_my}/build/top/{url_enemy}"
        ugg = f"https://u.gg/lol/champions/{url_my}/build?opp={url_enemy}"
        google = f"https://www.google.com/search?q=site:lol-guide.com+{enemy_name_jp}+カウンター"

        b1, b2, b3 = st.columns(3)
        with b1: st.link_button("📘 LoL Guide (解説)", google, use_container_width=True)
        with b2: st.link_button("🔥 DeepLoL (OTP)", deeplol, use_container_width=True)
        with b3: st.link_button("📈 U.GG (統計)", ugg, use_container_width=True)

if __name__ == "__main__":
    main()