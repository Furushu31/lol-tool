import streamlit as st
import requests

# -----------------------------------------------------------
# 1. ページ設定 & デザイン (LOL.GG Style)
# -----------------------------------------------------------
st.set_page_config(page_title="LOL.GG", page_icon="⚔️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');
    .stApp { background-color: #0f0f0f; color: #e0e0e0; font-family: 'Roboto', sans-serif; }
    h1 { font-family: 'Bebas Neue', sans-serif; color: #c8aa6e; font-size: 4rem !important; text-align: center; margin-top: -20px; text-shadow: 0 0 20px rgba(200,170,110,0.4); }
    
    /* 検索パネル */
    .search-panel { background-color: #1e1e1e; padding: 20px; border-radius: 12px; border: 1px solid #444; margin-bottom: 20px; }
    .stSelectbox > label { color: #c8aa6e !important; font-size: 1.1rem !important; font-weight: bold; }
    
    /* ヒーローヘッダー */
    .hero-container { position: relative; width: 100%; border-radius: 12px; margin-bottom: 20px; border: 1px solid #333; overflow: hidden; }
    .hero-image { width: 100%; display: block; mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 50%, rgba(0,0,0,0) 100%); -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 50%, rgba(0,0,0,0) 100%); }
    .hero-overlay { position: absolute; bottom: 20px; left: 30px; text-shadow: 2px 2px 8px #000; }
    .hero-title { font-family: 'Bebas Neue', sans-serif; font-size: 4rem; color: #fff; line-height: 1; }

    /* スキルカード */
    .skill-card { background-color: #1a1a1a; border-radius: 8px; border: 1px solid #444; transition: transform 0.2s; margin-bottom: 10px; }
    .skill-card:hover { transform: translateY(-5px); border-color: #c8aa6e; }
    .skill-img { width: 100%; border-radius: 8px 8px 0 0; opacity: 0.9; }
    .skill-info { padding: 8px; text-align: center; }
    .skill-key { color: #c8aa6e; font-weight: bold; font-size: 0.8rem; }
    .skill-cd { color: white; font-weight: bold; font-size: 1.1rem; }

    /* Tips Box */
    .tips-box { background-color: #2a1a1a; border-left: 5px solid #ff4c4c; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    .tips-title { color: #ff4c4c; font-weight: bold; font-size: 1.2rem; margin-bottom: 5px; }
    .tips-text { font-size: 0.95rem; line-height: 1.5; color: #ddd; }

    /* ボタン */
    div.stButton > button { background-color: #333; color: white; border: 1px solid #555; font-weight: bold; height: 3em; }
    div.stButton > button:hover { border-color: #c8aa6e; color: #c8aa6e; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------
# データ取得
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
# 表示用関数
# -----------------------------------------------------------
def show_champion_data(champ_id, champ_name_jp, version, is_enemy=False):
    detail_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ja_JP/champion/{champ_id}.json"
    try:
        res = requests.get(detail_url).json()['data'][champ_id]
        spells = res['spells']
        passive = res['passive']
        enemy_tips = res.get('enemytips', [])
    except:
        st.error(f"Failed to load data for {champ_name_jp}")
        return

    # 壁紙
    role_text = "ENEMY THREAT" if is_enemy else "YOUR CHAMPION"
    splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_id}_0.jpg"
    st.markdown(f"""
    <div class="hero-container">
        <img src="{splash_url}" class="hero-image">
        <div class="hero-overlay">
            <div class="hero-title">{champ_id.upper()}</div>
            <p style="color:#ccc; font-size: 1.2rem;">{role_text}: {champ_name_jp}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tips (相手のみ)
    if is_enemy and enemy_tips:
        st.markdown(f"""
        <div class="tips-box">
            <div class="tips-title">⚠ {champ_name_jp} 対策 (Riot公式Tips)</div>
            <div class="tips-text">
                <ul>{''.join([f'<li>{tip}</li>' for tip in enemy_tips])}</ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # スキル
    st.caption(f"📊 SKILL COOLDOWN (Patch {version})")
    cols = st.columns(5)
    
    # Passive
    with cols[0]:
        pas_img = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/passive/{passive['image']['full']}"
        st.markdown(f"""
        <div class="skill-card">
            <img src="{pas_img}" class="skill-img">
            <div class="skill-info"><div class="skill-key">P</div><div class="skill-cd" style="font-size:1rem;">-</div></div>
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
                <div class="skill-info"><div class="skill-key">{keys[i]}</div><div class="skill-cd">{cd_text}</div></div>
            </div>
            """, unsafe_allow_html=True)
    st.divider()

# -----------------------------------------------------------
# メイン処理
# -----------------------------------------------------------
def main():
    st.markdown("<h1>LOL.GG</h1>", unsafe_allow_html=True)
    version, champ_list, id_map = load_data()
    if not version: return

    # 検索パネル
    with st.container():
        st.markdown('<div class="search-panel">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🔵 Your Pick")
            my_choice = st.selectbox("自分", champ_list, index=None, label_visibility="collapsed", placeholder="自分...")
        with c2:
            st.markdown("#### 🔴 Enemy Pick")
            enemy_choice = st.selectbox("相手", champ_list, index=None, label_visibility="collapsed", placeholder="相手...")
        st.markdown('</div>', unsafe_allow_html=True)

    # 1. 両方選択 (マッチアップ)
    if my_choice and enemy_choice:
        my_id = id_map[my_choice]
        enemy_id = id_map[enemy_choice]
        enemy_name_jp = enemy_choice.split(" (")[0]
        
        show_champion_data(enemy_id, enemy_name_jp, version, is_enemy=True)

        st.subheader("🚀 Matchup Guides")
        url_my = "wukong" if my_id == "MonkeyKing" else my_id.lower()
        url_enemy = "wukong" if enemy_id == "MonkeyKing" else enemy_id.lower()
        
        deeplol = f"https://www.deeplol.gg/champions/{url_my}/build/top/{url_enemy}"
        ugg = f"https://u.gg/lol/champions/{url_my}/build?opp={url_enemy}"
        lolps = f"https://lol.ps/champ/{url_my}/statistics/" # LOL.PSは自分の統計ページへ
        google = f"https://www.google.com/search?q=site:lol-guide.com+{enemy_name_jp}+カウンター"

        b1, b2, b3, b4 = st.columns(4)
        with b1: st.link_button("📘 解説 (LoL Guide)", google, use_container_width=True)
        with b2: st.link_button("🔥 OTP (DeepLoL)", deeplol, use_container_width=True)
        with b3: st.link_button("📈 統計 (U.GG)", ugg, use_container_width=True)
        with b4: st.link_button("🇰🇷 メタ (LOL.PS)", lolps, use_container_width=True)

    # 2. 相手だけ選択 (カウンター確認)
    elif enemy_choice:
        enemy_id = id_map[enemy_choice]
        enemy_name_jp = enemy_choice.split(" (")[0]
        show_champion_data(enemy_id, enemy_name_jp, version, is_enemy=True)

        st.subheader("🛡️ Counter Info")
        url_enemy = "wukong" if enemy_id == "MonkeyKing" else enemy_id.lower()
        
        # U.GG Counters (最も信頼性が高い)
        ugg_counter = f"https://u.gg/lol/champions/{url_enemy}/counter"
        # LOL.PS (韓国メタ)
        lolps_link = f"https://lol.ps/champ/{url_enemy}/statistics/"

        b1, b2 = st.columns(2)
        with b1: st.link_button("📉 U.GG (有利不利リスト)", ugg_counter, type="primary", use_container_width=True)
        with b2: st.link_button("🇰🇷 LOL.PS (韓国統計)", lolps_link, use_container_width=True)

    # 3. 自分だけ選択 (ビルド確認)
    elif my_choice:
        my_id = id_map[my_choice]
        my_name_jp = my_choice.split(" (")[0]
        show_champion_data(my_id, my_name_jp, version, is_enemy=False)

        st.subheader("🛠️ Build Guides")
        url_my = "wukong" if my_id == "MonkeyKing" else my_id.lower()
        
        ugg_build = f"https://u.gg/lol/champions/{url_my}/build"
        deeplol_build = f"https://www.deeplol.gg/champions/{url_my}/build"
        lolps_build = f"https://lol.ps/champ/{url_my}/statistics/"

        b1, b2, b3 = st.columns(3)
        with b1: st.link_button("📈 U.GG (基本ビルド)", ugg_build, use_container_width=True)
        with b2: st.link_button("🔥 DeepLoL (OTP)", deeplol_build, use_container_width=True)
        with b3: st.link_button("🇰🇷 LOL.PS (韓国)", lolps_build, use_container_width=True)

if __name__ == "__main__":
    main()
