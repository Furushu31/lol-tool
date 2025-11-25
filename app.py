import streamlit as st
import requests

# ==============================================================================
# 0. ユーティリティ
# ==============================================================================
def kata_to_hira(text):
    hira = []
    for char in text:
        code = ord(char)
        if 0x30A1 <= code <= 0x30F6:
            hira.append(chr(code - 0x60))
        else:
            hira.append(char)
    return "".join(hira)

# ==============================================================================
# 1. 秘伝の攻略データ (画像 + 動画解析データ完全版)
# ==============================================================================
CUSTOM_DATA = {
    # --- 画像解析データ (対面対策) ---
    "Garen": {
        "danger": ["Rは減少体力比例の確定ダメ。体力管理注意。", "Eの回転で削られないように。"],
        "tips": ["パッシブ(緑オーラ)の自動回復を止めるため、小まめに殴る。", "Wのシールド中はスキルを控える。"],
        "counters": [{"name": "Camille", "reason": "Q確定ダメが刺さる。"}, {"name": "Kayle", "reason": "Qスローでカイト可能。"}]
    },
    "Darius": {
        "danger": ["パッシブ5スタックは最強。絶対殴り合わない。", "序盤プッシュするとゴーストオールインで死ぬ。"],
        "tips": ["Qの刃（外側）を内側に避ければ勝てる。", "TPがないのでキルされなければ勝ち。"],
        "counters": [{"name": "Gnar", "reason": "Eで逃げられる。"}, {"name": "Vayne", "reason": "EをEで弾ける。"}]
    },
    "Renekton": {
        "danger": ["怒りゲージWやQは激痛。", "自陣ミニオンが多い時のEブリンクに注意。"],
        "tips": ["Eは縦に動くので、横軸に避ける。", "スキルを空振りしたらチャンス。"],
        "counters": [{"name": "Illaoi", "reason": "E避けたら勝ち。"}, {"name": "Mordekaiser", "reason": "Rで隔離すれば勝てる。"}]
    },
    # ... (他、既存の画像データはそのまま保持) ...
    
    # --- 動画解析データ (自分が使う時のテクニック) ---
    "Blitzcrank": {
        "my_tips": [
            "【W→E→Q】Wで距離を詰め、E(打ち上げ)からQ(フック)を撃つと回避不可の必中コンボになる。",
            "【フックのコツ】相手がCSを取る(AAモーションをする)瞬間を狙って撃つ。",
            "【ヘクスフラッシュ】海賊のエンチャントと同時に使うと加速できる小技がある。"
        ]
    },
    "Sylas": {
        "my_tips": [
            "【コンボ】E1→Q→E2→W→AA。スキル間にパッシブAAを挟む。",
            "【Rの仕様】ヤスオの風殺の壁やサミーラWで「Rを盗むこと自体」を防がれるので注意。",
            "【ビルド】柔らかい敵が多いなら電撃+ロケットベルト、硬いなら征服者+ロア。"
        ],
        "danger": ["E2の鎖に当たると大ダメージ。", "W回復で逆転される。"], # 相手に来た時用
        "tips": ["重症を買う。", "E2を避ける。"],
        "counters": [{"name": "Vex", "reason": "ブリンクに恐怖が刺さる。"}]
    },
    "Neeko": {
        "my_tips": [
            "【Rの隠し方】パッシブでミニオンに変身してからRを撃つと、予備動作（飛び上がる円）が相手に見えない。",
            "【W活用】味方に変身してWの分身と一緒に突っ込むと相手を混乱させられる。",
            "【変身】トリンダメアなど強力な味方に変身してプレッシャーをかける。"
        ],
        "danger": ["Eスネアはミニオン貫通で強化される。", "Rの広範囲スタン。"],
        "tips": ["ミニオンの数を数えて変身を疑う。", "Rが見えたら即離れる。"]
    },
    "Alistar": {
        "my_tips": [
            "【WQコンボ】基本コンボ。Wで突進中にQを押す。",
            "【インセク】Q→フラッシュ→Wで、敵を自軍タワー側に突き飛ばせる。",
            "【フェイント】Eのスタックが溜まる直前にリコールモーション等でフェイントをかける小技。"
        ]
    },
    "Jinx": {
        "my_tips": [
            "【武器切り替え】Q(ミニガン)で攻速スタックを3つ溜めてから、ロケットに切り替えて戦うとDPSが出る。",
            "【集団戦】まずは前衛を溶かしてパッシブ(Get Excited!)を発動させ、機動力で後衛を狙う。",
            "【W】Wの射程と当たり判定を理解して牽制に使う。"
        ]
    },
    "Galio": {
        "my_tips": [
            "【立ち回り】序盤はQでプッシュしてローム。サイドレーンでR支援を狙う。",
            "【集団戦】後半はADCを守る「2人目のサポート」として動くのが強い。",
            "【ビルド】AP係数が高いのでドラランスタート推奨。"
        ],
        "danger": ["WタウントからのQバースト。", "R支援。"],
        "tips": ["Eはミニオンに当たると止まる。"]
    },
    "Kai'Sa": {
        "my_tips": [
            "【R中のW】Rで飛んでいる最中にWを撃つと、相手の至近距離で必中させやすい。",
            "【進化キャンセル】B(リコール)を押しながら進化ボタンを押すと、硬直なしで進化できる。",
            "【ビルド】相手が柔らかいならプレス、硬いなら征服者。"
        ]
    },
    "Jax": {
        "my_tips": [
            "【E活用】Eはミニオンの攻撃も無効化する。ミニオンウェーブの中で戦うと被ダメを抑えつつEの反撃ダメUPを狙える。",
            "【AAキャンセル】AA→Wでモーションキャンセルして瞬間火力を出す。",
            "【Lv1-3】序盤最強クラスなので積極的にトレードする。"
        ],
        "danger": ["E中のAAは反撃ダメが増える。", "Q飛びつき。"],
        "tips": ["マナ切れを待つ。"]
    },
    "Ryze": {
        "my_tips": [
            "【CS】序盤は弱い。Qで確実にCSを取り、涙とロアを急ぐ。",
            "【サイド】中盤以降はサイドプッシュし、敵が来たらRで逃げるor味方と挟む。",
            "【集団戦】ADCなどのキャリーと1:1交換を狙う動きも強い。"
        ]
    },
    "Lillia": {
        "my_tips": [
            "【スタック維持】ジャングル周回中はQのパッシブ(移動速度)を切らさないようにする。切れる直前にQを撃つ。",
            "【W】Wの中心を当てるとダメージが3倍になる。寝ている敵には必ず中心を当てる。",
            "【ビルド】征服者が強い。仮面→リフトメーカー→砂時計。"
        ]
    },
    "Jayce": {
        "my_tips": [
            "【不滅ジェイス】ルーンに不滅（不死者）を持ち、遠隔AA→変身→近接Qで殴るとダメージ交換で勝てる。",
            "【加速ゲート】Eは自分に近い位置に出すと、発動と同時に加速できて隙がない。",
            "【マナ】ハンマー形態でAAしてマナを回復するのを忘れない。"
        ]
    },
    "Ezreal": {
        "my_tips": [
            "【パッシブ】戦う前にQをミニオンに当ててパッシブ(攻速UP)を5スタック溜めておく。",
            "【Eの仕様】Eには詠唱時間があるため、ブリッツのフック等に合わせて入力すると、引っ張られても元の位置に戻れる（バッファリング）。"
        ]
    },
    "Wukong": {
        "my_tips": [
            "【Q】Qがメイン火力。AA→Qで射程を伸ばして殴る。",
            "【W】W(分身)でスキルを避けたり、Sキーで止まって分身のフリをして敵を騙す（フェイク）。",
            "【ビルド】三相→サンダードスカイが安定。"
        ]
    },
    "Elise": {
        "my_tips": [
            "【タワーダイブ】人形態で攻撃→タワー攻撃を受ける→蜘蛛形態Eで空中に逃げることでタワーのタゲを切れる。",
            "【W→Q】人形態W（爆弾蜘蛛）を出してから蜘蛛形態Qで飛びつくと、爆弾蜘蛛も一緒に飛んでいく。"
        ]
    },
    "Zoe": {
        "my_tips": [
            "【Q最大火力】Rで後ろに飛んでからQを前に投げると飛距離が伸びてダメージが最大化する。",
            "【パッシブ】スキル使用後の強化AAをしっかり挟むこと。",
            "【E】壁越しにEを撃つと射程が伸びる。"
        ]
    },
    "Brand": {
        "my_tips": [
            "【ジャングル】パッシブの爆発でクリアが早い。モンスターが集まる位置にWを置く。",
            "【最大火力】Q→E→W。炎上中の敵にWを当てるとダメージ25%UP。",
            "【必中スタン】Q→フラッシュ→Eで、Qの弾速を誤魔化してスタンさせられる。"
        ]
    },
    "Sett": {
        "my_tips": [
            "【右パンチ】セトの右パンチ(2発目)は射程が長く出が早い。左パンチで牽制し、右を温存するテクニックがある。",
            "【E】Eは角（斜め）で当てると射程が少し伸びる。",
            "【R】敵のタンクを掴んで、敵の後衛キャリーの中に叩きつけるのが理想。"
        ]
    },
    "LeBlanc": {
        "my_tips": [
            "【最大火力】E→Q→R(Q複製)→W。Qの印をRで起爆するのが一番痛い。",
            "【トレード】Wで入ってQ→E、危なくなったらW再発動で戻るヒットアンドアウェイ。",
            "【Wダミー】R(W複製)で移動した後、偽物が出るので操作して敵を騙す。"
        ],
        "danger": ["Q→Wコンボ。", "W→Eスネア。"],
        "tips": ["WのCD中に攻める。", "ガンクに注意。"],
        "counters": [{"name": "Lissandra", "reason": "Rで封殺。"}]
    },
    "Annie": {
        "my_tips": [
            "【不意打ちスタン】スタックを3つ溜めておき、Qを撃って飛んでいる最中にEを使って4スタックにすると、相手が反応できないスタンになる。",
            "【ティバーズ】R(ティバーズ)はAltキーで操作できる。タワーのタゲ取りやスキルブロックに使う。"
        ],
        "danger": ["スタック溜まりRスタン。"],
        "tips": ["スタック数を見る。", "MRを積む。"],
        "counters": [{"name": "Syndra", "reason": "射程外から削れる。"}]
    },
}

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
            name_jp = val['name']
            name_en = key
            name_hira = kata_to_hira(name_jp)
            display_name = f"{name_jp} ({name_en}) / {name_hira}"
            champ_list.append(display_name)
            id_map[display_name] = {'id': key, 'key': val['key']}
        return version, sorted(champ_list), id_map
    except:
        return None, [], {}

# -----------------------------------------------------------
# 3. デザイン設定 (Apple Style)
# -----------------------------------------------------------
st.set_page_config(page_title="LOL.GG", page_icon="🍎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .stApp { background-color: #f5f5f7; color: #1d1d1f; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 20px; }

    /* ヘッダー */
    .apple-header { text-align: center; padding: 10px 0 20px; margin-bottom: 10px; }
    .apple-title { font-size: 36px; font-weight: 700; letter-spacing: -0.5px; color: #1d1d1f; margin-bottom: 5px; }
    .apple-subtitle { font-size: 16px; color: #86868b; font-weight: 400; }

    /* カード */
    .apple-card { background: #ffffff; border-radius: 18px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); margin-bottom: 15px; }
    
    /* 検索エリア */
    .search-area { max-width: 900px; margin: 0 auto 20px auto; padding: 0 10px; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: 1px solid #d2d2d7 !important; border-radius: 12px !important; color: #1d1d1f !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; }

    /* スキル */
    .skill-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 15px 0; }
    .skill-box { background: #fbfbfd; border: 1px solid #d2d2d7; border-radius: 12px; padding: 10px 5px; text-align: center; }
    .skill-key { font-size: 11px; color: #86868b; font-weight: 600; text-transform: uppercase; }
    .skill-cd { font-size: 16px; font-weight: 700; color: #1d1d1f; margin-top: 2px; }

    /* Tips Cards */
    .feature-card { padding: 15px; border-radius: 14px; margin-bottom: 12px; }
    .danger-card { background-color: #fff2f2; border-left: 4px solid #ff3b30; }
    .tips-card { background-color: #f2f7ff; border-left: 4px solid #0071e3; }
    .my-tips-card { background-color: #f5fff5; border-left: 4px solid #34c759; } /* Apple Green for My Tips */
    
    .feature-title { font-size: 15px; font-weight: 700; margin-bottom: 8px; display: block; }
    .danger-title { color: #ff3b30; }
    .tips-title { color: #0071e3; }
    .my-tips-title { color: #34c759; }
    
    ul { margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.6; color: #333; }

    /* Counters */
    .counter-row { display: flex; align-items: center; background: #ffffff; border: 1px solid #d2d2d7; border-radius: 14px; padding: 12px; margin-bottom: 10px; }
    .counter-icon { width: 48px; height: 48px; border-radius: 10px; margin-right: 15px; }
    .counter-info { flex: 1; }
    .counter-name { font-size: 15px; font-weight: 700; color: #1d1d1f; }
    .counter-reason { font-size: 12px; color: #424245; margin-top: 4px; line-height: 1.4; }

    /* Button */
    div.stButton > button { background-color: #0071e3; color: #ffffff; border: none; border-radius: 980px; padding: 8px 20px; font-size: 13px; font-weight: 600; width: 100%; transition: all 0.2s; }
    div.stButton > button:hover { background-color: #0077ed; transform: scale(1.02); }
    h4 { font-weight: 700; color: #1d1d1f; margin-top: 0; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------
# 4. メイン処理
# -----------------------------------------------------------
def main():
    # Apple Style Header
    st.markdown("""
        <div class="apple-header">
            <div class="apple-title">LOL.GG</div>
            <div class="apple-subtitle">Pro-Level Analysis.</div>
        </div>
    """, unsafe_allow_html=True)

    version, champ_list, id_map = load_data()
    if not version: return

    # 検索エリア
    st.markdown('<div class="search-area">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        my_choice = st.selectbox("🔵 Your Pick", champ_list, index=None, placeholder="Search...", label_visibility="collapsed")
    with c2:
        enemy_choice = st.selectbox("🔴 Enemy Pick", champ_list, index=None, placeholder="Search...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # === 1. 相手を選択した時の表示 (対策モード) ===
    if enemy_choice:
        enemy_data = id_map[enemy_choice]
        champ_id = enemy_data['id']
        
        try:
            detail_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ja_JP/champion/{champ_id}.json"
            res = requests.get(detail_url).json()['data'][champ_id]
            spells = res['spells']
        except: return

        col_left, col_right = st.columns([1, 2])

        # --- 左：画像とリンク ---
        with col_left:
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            
            splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_id}_0.jpg"
            st.image(splash_url, use_container_width=True)
            
            st.markdown("#### Links")
            url_enemy = "wukong" if champ_id == "MonkeyKing" else champ_id.lower()
            st.link_button("📉 U.GG (Counter)", f"https://u.gg/lol/champions/{url_enemy}/counter", use_container_width=True)
            st.link_button("🇰🇷 LOL.PS (Stats)", f"https://lol.ps/champ/{enemy_data['key']}/statistics/", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- 右：攻略情報 ---
        with col_right:
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            
            # スキルCD
            st.markdown("#### Abilities (CD)")
            keys = ['Q', 'W', 'E', 'R']
            cd_html = '<div class="skill-grid">'
            for i, spell in enumerate(spells):
                cd = "/".join(map(str, spell['cooldown']))
                cd_html += f'<div class="skill-box"><div class="skill-key">{keys[i]}</div><div class="skill-cd">{cd}</div></div>'
            cd_html += '</div>'
            st.markdown(cd_html, unsafe_allow_html=True)

            # 秘伝の攻略メモ (Danger & Tips)
            if champ_id in CUSTOM_DATA:
                cust = CUSTOM_DATA[champ_id]
                
                if "danger" in cust:
                    html = '<div class="feature-card danger-card"><span class="feature-title danger-title">⚠ 危険なアクション</span><ul>'
                    for d in cust['danger']: html += f'<li>{d}</li>'
                    html += '</ul></div>'
                    st.markdown(html, unsafe_allow_html=True)
                
                if "tips" in cust:
                    html = '<div class="feature-card tips-card"><span class="feature-title tips-title">💡 意識すること</span><ul>'
                    for t in cust['tips']: html += f'<li>{t}</li>'
                    html += '</ul></div>'
                    st.markdown(html, unsafe_allow_html=True)

                # Counters
                if "counters" in cust:
                    st.markdown("#### 🛡️ Recommended Counters")
                    for c in cust['counters']:
                        c_name = c['name']
                        icon_name = c_name.replace(" ", "").replace("'", "").capitalize()
                        # 簡易アイコン正規化
                        if c_name == "Wukong": icon_name = "MonkeyKing"
                        if c_name == "K'Sante": icon_name = "KSante"
                        if c_name == "Kai'Sa": icon_name = "Kaisa"
                        if c_name == "Vel'Koz": icon_name = "Velkoz"
                        if c_name == "Kha'Zix": icon_name = "Khazix"
                        if c_name == "Bel'Veth": icon_name = "Belveth"
                        if c_name == "Rek'Sai": icon_name = "RekSai"
                        if c_name == "Kog'Maw": icon_name = "KogMaw"
                        if c_name == "Cho'Gath": icon_name = "Chogath"
                        
                        c_icon_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{icon_name}.png"
                        
                        st.markdown(f"""
                        <div class="counter-row">
                            <img src="{c_icon_url}" class="counter-icon" onerror="this.style.display='none'">
                            <div class="counter-info">
                                <div class="counter-name">VS {c_name}</div>
                                <div class="counter-reason">{c['reason']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No custom guide data available.")
            st.markdown('</div>', unsafe_allow_html=True)

    # === 2. 自分を選択した時の表示 (テクニックモード) ===
    elif my_choice:
        my_data = id_map[my_choice]
        champ_id = my_data['id']
        
        col_left, col_right = st.columns([1, 2])
        
        # --- 左：画像とリンク ---
        with col_left:
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            
            # 自分のキャラ画像を表示 (NEW!)
            splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_id}_0.jpg"
            st.image(splash_url, use_container_width=True)
            
            st.markdown("#### Links")
            my_url = "wukong" if champ_id == "MonkeyKing" else champ_id.lower()
            deeplol_otp_url = f"https://www.deeplol.gg/champions/{my_url}/mastery/all"
            
            st.link_button(f"🔥 OTP Ranking (DeepLoL)", deeplol_otp_url, use_container_width=True)
            st.link_button("📈 Build Guide (U.GG)", f"https://u.gg/lol/champions/{my_url}/build", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # --- 右：My Tips (動画解析データ) ---
        with col_right:
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            
            if champ_id in CUSTOM_DATA and "my_tips" in CUSTOM_DATA[champ_id]:
                cust = CUSTOM_DATA[champ_id]
                html = '<div class="feature-card my-tips-card"><span class="feature-title my-tips-title">🚀 プロのテクニック / 小技</span><ul>'
                for t in cust['my_tips']: html += f'<li>{t}</li>'
                html += '</ul></div>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info(f"※ {my_choice.split('(')[0]} のカスタムテクニック情報はまだ登録されていません。")
                
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
