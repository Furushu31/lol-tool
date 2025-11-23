import streamlit as st
import requests

# ==============================================================================
# 0. 秘伝の攻略データ (画像解析済み)
# ==============================================================================
CUSTOM_DATA = {
    "Garen": {
        "danger": ["Rは減少体力比例の確定ダメ。体力管理注意。", "Eの回転で削られないように。"],
        "tips": ["パッシブ(緑オーラ)の自動回復を止めるため、小まめに殴る。", "Wのシールド中はスキルを控える。"],
        "counters": [
            {"name": "Camille", "reason": "Qの確定ダメが刺さる。Q2を待機して殴る。"},
            {"name": "Kayle", "reason": "Q突進にQスローorW加速で対処可能。RをRで無効化。"},
        ]
    },
    "Darius": {
        "danger": ["パッシブ5スタックは最強。絶対殴り合わない。", "序盤プッシュするとゴーストオールインで死ぬ。", "Lv1ブッシュ待機に注意。"],
        "tips": ["TPがないので、キルされなければ勝ち（CS負けてもOK）。", "Qの刃（外側）を内側に避ければ勝てる。"],
        "counters": [
            {"name": "Gnar", "reason": "Eで引っ張られてもEで逃げられる。スロウ漬けにできる。"},
            {"name": "Vayne", "reason": "EをEで弾ける。スペル差がないならカイトし放題。"},
            {"name": "Aatrox", "reason": "Q先端当てとEの機動力でダリウスQをかわせる。"},
        ]
    },
    "Renekton": {
        "danger": ["怒りゲージが溜まっている時のWやQは激痛。", "自陣ミニオンが多い時のEブリンクに注意。"],
        "tips": ["Eは縦に動くので、横軸に避ける。", "スキルを空振りしたら長いCDの間がチャンス。"],
        "counters": [
            {"name": "Illaoi", "reason": "Eを避けたらタコ殴り。イラオイの回復が高くレネクトンのバーストを耐える。"},
            {"name": "Mordekaiser", "reason": "Wシールドで耐え、Rで隔離すればボコボコにできる。"},
        ]
    },
    "Jax": {
        "danger": ["E(風車)中にAAすると反撃ダメージが増える。", "Qで飛びついてからのオールイン。"],
        "tips": ["マナが枯渇しやすい(Q65)。ビスケットがないのでマナ切れを待つ。", "Eがない時間は非常に脆い。"],
        "counters": [
            {"name": "Kennen", "reason": "スタンスタックがあればQ飛びつきをEWで返り討ちにできる。"},
            {"name": "Poppy", "reason": "Q飛びつきをWで撃墜できる。"},
        ]
    },
    "Kennen": {
        "danger": ["パッシブ1スタックある時に近づくとEWで即スタン。", "Rの範囲スタンは集団戦で脅威。"],
        "tips": ["プッシュされると弱い。タワー下に押し込みたい。", "ハラスが痛いのでリコールまで耐える意識。"],
        "counters": [
            {"name": "Nasus", "reason": "エアリーE上げでE当てるだけで勝てる。WでAS低下させれば無力。"},
            {"name": "Malphite", "reason": "Qハラスだけで削り切れる。Rのガンク合わせで必殺。"},
        ]
    },
    "Jayce": {
        "danger": ["ハンマーQからのオールインバースト。", "序盤に差をつけられるとスノーボールされる。"],
        "tips": ["キャリーし切るのが難しいキャラなので、腐らず中盤以降のキャッチを狙う。", "ガンクに弱い。"],
        "counters": [
            {"name": "Malphite", "reason": "パッシブシールドでハラス無効。Qハラス＆Rワンコンで勝てる。"},
            {"name": "Gragas", "reason": "キャノン変形直後やハンマーEがない時にRで引き寄せれば勝ち。"},
        ]
    },
    "Camille": {
        "danger": ["E(壁ドン)からのガンク合わせが超強力。", "Q2(確定ダメ)の準備ができたら下がる。"],
        "tips": ["壁際に立たない（Eが当たりやすくなる）。", "パッシブシールドの属性(物理/魔法)を見る。"],
        "counters": [
            {"name": "Gwen", "reason": "Q中心の確定ダメが刺さる。WでカミールRを無効化も可能。"},
            {"name": "Renekton", "reason": "Wシールド破壊が刺さる。Eで入ってきてもRで返り討ち。"},
            {"name": "Jax", "reason": "Q強化AAをEで無効化できる。壁ドンEもEスタンで止められる。"},
        ]
    },
    "Irelia": {
        "danger": ["パッシブ4スタック時は最強。殴り合うな。", "ミニオンをQで飛び回って翻弄してくる。", "王剣完成時はパワースパイク。"],
        "tips": ["Eは横に避ける。", "QがCDになったら無力なので攻める。"],
        "counters": [
            {"name": "Renekton", "reason": "W強化でシールド破壊。近接殴り合いなら負けない。"},
            {"name": "Jax", "reason": "EでイレリアのAA(主火力)を全て防げる。ハードカウンター。"},
            {"name": "Tryndamere", "reason": "殴り合い最強。Rで死なないのでイレリアのバーストを耐えて倒せる。"},
        ]
    },
    "Aatrox": {
        "danger": ["Qのスイートスポット(先端)に当たるとノックアップ。", "R変身中の回復量が異常。"],
        "tips": ["Q1,Q2,Q3の合間に懐に入るか、横に避ける。", "重症(回復阻害)アイテム必須。"],
        "counters": [
            {"name": "Kled", "reason": "Qの重症が刺さる。Eで懐に潜り込めるのでQを避けやすい。"},
            {"name": "Camille", "reason": "Qの加速でエイトロックスQを避け、RでQ3を回避できる。"},
        ]
    },
    "Sion": {
        "danger": ["死んだ後のゾンビパッシブが痛い。倒してもすぐ逃げる。", "草むらからの溜めQノックアップ。"],
        "tips": ["序盤は柔らかいので積極的に殴る。", "Eの咆哮を食らうとARが下がるので注意。"],
        "counters": [
            {"name": "Darius", "reason": "足が遅いサイオンをEで捕まえて出血スタックで倒し切れる。"},
            {"name": "Aatrox", "reason": "Qのノックアップでサイオンの溜めQを中断させられる。"},
        ]
    },
    "Gangplank": {
        "danger": ["樽(E)の連鎖爆発。ブッシュに樽を隠していることが多い。", "パッシブ(火刀)のAAは確定ダメで痛い。"],
        "tips": ["樽のゲージ(HP下のメモリ)をよく見る。", "W(オレンジ)でCC解除されるのでCCのタイミング注意。"],
        "counters": [
            {"name": "Rumble", "reason": "Wシールドでハラス軽減。イグナイトE2発でオーバーヒート殴りで勝てる。"},
            {"name": "Aatrox", "reason": "ブリンクがないGPはAatroxのフルコンボを避けられない。"},
        ]
    },
    "Nasus": {
        "danger": ["イグナイト持ちが多い。CS欲張ると死ぬ。", "Lv6のR変身時の殴り合いは強力。"],
        "tips": ["Eハラスしてくるならマナ切れを待つ。", "Qスタックを溜めさせないようにゾーニング。"],
        "counters": [
            {"name": "Malphite", "reason": "EでAS低下させればナサスのQ回転率が落ちる。集団戦での貢献度で勝つ。"},
            {"name": "Quinn", "reason": "Eで距離を取り、Qで視界を奪えばナサスは近づけない。"},
        ]
    },
    "Malphite": {
        "danger": ["Lv6以降のRワンコン。HP6割は即死圏内。", "Qハラスで削られてからのオールイン。"],
        "tips": ["パッシブシールドが復活しないよう小まめに殴る。", "E(地面叩き)を使ったらAS低下するので殴り合わない。"],
        "counters": [
            {"name": "Sylas", "reason": "強力なマルファイトRを奪える。W回復でハラスに耐えられる。"},
            {"name": "Mordekaiser", "reason": "硬いのでワンコンで死なない。Rで閉じ込めればマルファイトは逃げ場がない。"},
        ]
    },
    "Quinn": {
        "danger": ["イグナイト持ち。序盤のキルポテンシャルが高い。", "マークが付いた時のAAが痛い。"],
        "tips": ["Eで距離を取られるので、ブリンクはEの後まで温存。", "Lv6以降のロームが早い。"],
        "counters": [
            {"name": "Malphite", "reason": "QハラスとRワンコンで柔らかいクインを粉砕できる。"},
            {"name": "Nasus", "reason": "W(ウィザー)をかければAA主体のクインは機能停止する。"},
        ]
    },
    "Udyr": {
        "danger": ["Lv1のR(不死鳥)は最強クラス。絶対殴り合わない。", "覚醒Rのスロウとダメージ。"],
        "tips": ["序盤耐えれば後半失速する。", "ミニオン越しにRを当てられない位置取りをする。"],
        "counters": [
            {"name": "Darius", "reason": "殴り合い最強。足の遅いウディアをEで捕まえられる。"},
            {"name": "Kennen", "reason": "近づかれてもEで逃げられる。Rでカウンター可能。"},
        ]
    },
    "Olaf": {
        "danger": ["HPが減るほどASとLSが上がる。瀕死でも油断禁物。", "Lv1の斧投げハラス。"],
        "tips": ["Qの斧を拾わせない位置で戦う。", "Qは後ろではなく「横」に避ける。"],
        "counters": [
            {"name": "Tryndamere", "reason": "Rの無敵中はオラフも倒せない。殴り合いで勝てる。"},
            {"name": "Akali", "reason": "W煙幕でオラフのAAを防げる。機動力で翻弄できる。"},
        ]
    },
    "Gragas": {
        "danger": ["タワー付近でのR(樽爆破)引き寄せ。", "E(ボディスラム)の判定が強い。"],
        "tips": ["序盤はマナがきついので、スキルを使わせてマナ切れを狙う。", "パッシブ回復を許さない。"],
        "counters": [
            {"name": "Aatrox", "reason": "サステインでグラガスのハラスに耐えられる。"},
            {"name": "Gnar", "reason": "EジャンプでグラガスEをかわせる。レンジ差でいじめられる。"},
        ]
    },
    "Gwen": {
        "danger": ["Rのスロウからのオールイン。", "Q中心の確定ダメージ。"],
        "tips": ["W(霧)を使われたら中に入るか下がる。", "Qスタックがない時は弱い。"],
        "counters": [
            {"name": "Kennen", "reason": "レンジ有利。入ってきてもEで逃げ、Rで返り討ち。"},
            {"name": "Akali", "reason": "W煙幕でグウェンのAAを防げる。バーストで溶かせる。"},
        ]
    },
    "Kled": {
        "danger": ["非騎乗時のQ銃撃で勇気が溜まると再騎乗してHP回復する。", "Wの高速4回攻撃。"],
        "tips": ["WがCDの時（武器が光ってない時）に戦う。", "降りたクレッドはバーストで一気に倒す。"],
        "counters": [
            {"name": "Fiora", "reason": "Qの引っ張りをWパリィで無効化＆スタンできる。"},
            {"name": "Jax", "reason": "Wの4回攻撃をEで全て回避できる。ハードカウンター。"},
        ]
    },
    "Illaoi": {
        "danger": ["Eで魂を抜かれたら範囲外へ逃げる（殴り合うと死ぬ）。", "R使用後は触手の叩きつけが早くなる。"],
        "tips": ["触手をこまめに処理する。", "Eをミニオン越しに避ける。外したらチャンス。"],
        "counters": [
            {"name": "Gnar", "reason": "レンジ有利で触手を壊しやすい。Eを避けやすい。"},
            {"name": "Mordekaiser", "reason": "Rで異界に連れ込めば、設置した触手が消滅する。"},
        ]
    },
    "Yone": {
        "danger": ["Eで霊体化してからの一方的なトレード。", "Q3(風)がある時の飛び込み。"],
        "tips": ["Eの戻り位置を狙う。", "Rは発生が遅いので横に避ける。"],
        "counters": [
            {"name": "Vex", "reason": "ブリンクに対してパッシブ恐怖が発動する。"},
            {"name": "Renekton", "reason": "W強化でシールドを割りつつスタン。近接最強。"},
        ]
    },
    "Yasuo": {
        "danger": ["ミニオンを伝ってのE接近。", "風殺の壁(W)でスキルを消される。"],
        "tips": ["パッシブシールドをAAで剥がしてからスキルを撃つ。", "Q3(竜巻)は横移動で避ける。"],
        "counters": [
            {"name": "Renekton", "reason": "強化Wでシールド破壊。殴り合いで圧倒できる。"},
            {"name": "Lissandra", "reason": "Wのスネアでヤスオの機動力を封じられる。"},
        ]
    },
    "Zed": {
        "danger": ["W影からのQ手裏剣ハラス。", "Lv6 Rからのオールインバースト。"],
        "tips": ["Wの影が出ている間は距離を取る。", "Rを使われたら後ろにフラッシュしない（影に戻られる）。"],
        "counters": [
            {"name": "Garen", "reason": "Wでバースト軽減。沈黙でスキルを封じられる。"},
            {"name": "Diana", "reason": "Wシールドでハラスに耐え、殴り合いで勝てる。"},
        ]
    },
    "Fizz": {
        "danger": ["E(古の妖術)の無敵でスキルを避けられる。", "Rの魚がくっつくと大ダメージ。"],
        "tips": ["Eを使った後の着地を狙う。", "Lv1-2はいじめられるがLv3から強力。"],
        "counters": [
            {"name": "Lissandra", "reason": "R(自分)でフィズのRを無効化できる。Wで足止め可能。"},
            {"name": "Sylas", "reason": "Wの回復で殴り合いに勝てる。フィズRを奪って使える。"},
        ]
    },
    "Sylas": {
        "danger": ["E2の鎖に当たると大ダメージ＆スタン。", "Wの回復で瀕死から逆転される。"],
        "tips": ["重症(回復阻害)を買う。", "RでこちらのUltを奪われることを考慮する。"],
        "counters": [
            {"name": "Vex", "reason": "ブリンクに対して恐怖カウンター。"},
            {"name": "Taliyah", "reason": "Eの岩場を展開すればサイラスは飛び込めない。"},
        ]
    },
    "Viktor": {
        "danger": ["強化QのAAとシールド交換。", "強化Eの余波ダメージ。"],
        "tips": ["Eの射線上に立たない。", "ガンク耐性がないのでJGを呼ぶ。"],
        "counters": [
            {"name": "Irelia", "reason": "Qで懐に入り込めばビクターは逃げられない。"},
            {"name": "Yone", "reason": "RやEで距離を一気に詰められる。"},
        ]
    },
    "Talon": {
        "danger": ["W2段目の戻り＆パッシブ出血。", "壁越え(E)による予測不能なローム。"],
        "tips": ["姿が見えなくなったら即MIAピン。", "Wを使わせたら前に出る。"],
        "counters": [
            {"name": "Lissandra", "reason": "Rでバースト回避、Wで足止め。ローム阻止もしやすい。"},
            {"name": "Vex", "reason": "Q飛びつきをWで弾ける。"},
        ]
    },
    "Pantheon": {
        "danger": ["強化Wからのスタン＆バースト。", "E(盾)で無敵ガード。"],
        "tips": ["強化スタック(HP下のゲージ)が溜まっている時は下がる。", "Lv6以降のRロームに注意。"],
        "counters": [
            {"name": "Lissandra", "reason": "Wスタンに対してWやRでカウンター可能。"},
            {"name": "Orianna", "reason": "レンジ外から一方的に殴れる。"},
        ]
    },
    "Akali": {
        "danger": ["W(煙幕)の中での隠密行動。", "Eの手裏剣に当たると再発動で飛んでくる。"],
        "tips": ["煙幕中はスキルを撃たない（当たらない）。", "R1の飛びつきに注意。"],
        "counters": [
            {"name": "Galio", "reason": "W挑発でアカリを捕まえられる。魔法ダメシールドが有効。"},
            {"name": "Vex", "reason": "飛び回るアカリにパッシブ恐怖が刺さる。"},
        ]
    },
    "Galio": {
        "danger": ["WタウントからのQバースト。", "Rによる他レーンへの支援。"],
        "tips": ["E(正義の鉄拳)の突進はミニオンに当たると止まる。", "魔法シールドがあるのでAPチャンプは不利。"],
        "counters": [
            {"name": "Taliyah", "reason": "E突進をEの岩場で止められる。"},
            {"name": "AD Champions", "reason": "魔法シールドが無意味なADキャラ全般（トリス、ヨネなど）。"},
        ]
    },
    "Taliyah": {
        "danger": ["Wで岩場(E)に弾き飛ばされるコンボ。", "Qの連射ハラス。"],
        "tips": ["加工された地面(Qを使った場所)の上ではQが弱くなる。", "ミニオンの後ろに隠れる。"],
        "counters": [
            {"name": "Yone", "reason": "Eで岩場を無視して接近できる。"},
            {"name": "Kassadin", "reason": "魔法ダメ軽減パッシブとQシールドで耐えられる。"},
        ]
    },
    "Katarina": {
        "danger": ["短剣の落ちている場所に瞬歩(E)してくる。", "Rの回転刃によるAoEバースト。"],
        "tips": ["落ちている短剣に近づかない。", "Rを止めるCCを温存する。"],
        "counters": [
            {"name": "Galio", "reason": "W挑発やE打ち上げでカタリナRを即中断できる。"},
            {"name": "Vex", "reason": "瞬歩に合わせて恐怖を入れられる。"},
        ]
    },
    "Aurelion Sol": {
        "danger": ["Qのゲロ吐き継続ダメージ。", "スタックが溜まった後半のR衝撃波。"],
        "tips": ["Q中は足が止まるのでスキルを当てるチャンス。", "横に回り込むように動く。"],
        "counters": [
            {"name": "Yone", "reason": "Eで懐に入ればオレソルは逃げられない。"},
            {"name": "Fizz", "reason": "Eでスキルを回避しつつ飛び込める。"},
        ]
    },
    "Ahri": {
        "danger": ["E(チャーム)に当たるとフルコンボ確定。", "R(3回ブリンク)での追撃・逃げ。"],
        "tips": ["ミニオン越しにEは当たらない。", "Rがない時間は非常に弱い。"],
        "counters": [
            {"name": "Lissandra", "reason": "Rでアーリの機動力を封じ込められる。"},
            {"name": "Veigar", "reason": "Eの檻でブリンクを制限できる。"},
        ]
    },
    "Neeko": {
        "danger": ["Eのスネア（ミニオン貫通で強化）。", "Rの広範囲スタン。"],
        "tips": ["ミニオンに変身している可能性を疑う（ミニオン数を数える）。", "Rの予兆が見えたら即離れる。"],
        "counters": [
            {"name": "Lux", "reason": "射程外から一方的に攻撃できる。"},
            {"name": "Xerath", "reason": "圧倒的射程差で近づかせない。"},
        ]
    },
    "Cassiopeia": {
        "danger": ["Q毒状態でのE連打（超高DPS）。", "R(石化)を正面で食らうと死ぬ。"],
        "tips": ["Qを食らったら毒が切れるまで下がる。", "Rのタイミングで後ろを向く。"],
        "counters": [
            {"name": "Orianna", "reason": "レンジ外からボールで削れる。"},
            {"name": "Syndra", "reason": "射程有利。近づかれてもEで弾ける。"},
        ]
    },
    "Urgot": {
        "danger": ["Eで投げ飛ばされるとW(マシンガン)で溶かされる。", "RはHP25%以下で即死処刑。"],
        "tips": ["Eを避ければチャンス。予備動作に注意。", "Lv1から強いので殴り合わない。"],
        "counters": [
            {"name": "Mordekaiser", "reason": "ヒットボックスが大きくEを当てやすい。"},
            {"name": "Rammus", "reason": "W反射でアーゴットのWが自爆する（※Top運用時）。"},
        ]
    },
    "K'Sante": {
        "danger": ["Q3で引き寄せ→W→Rの壁ドンコンボ。", "オールアウト(R)中の確定ダメージ。"],
        "tips": ["壁際で戦わない。", "Q3が溜まっている時は距離を取る。"],
        "counters": [
            {"name": "Gwen", "reason": "確定ダメQでタンク装甲を貫通。Wで妨害無効。"},
            {"name": "Fiora", "reason": "CCをパリィして急所を突けば勝てる。"},
        ]
    },
    "Kayle": {
        "danger": ["Lv1のE連打（致命的テンポ）が意外と強い。", "Lv16以降の最強キャリー能力。"],
        "tips": ["Lv6まで弱いので徹底的にいじめる。", "R無敵中は殴らず位置調整。"],
        "counters": [
            {"name": "Irelia", "reason": "ブリンクで距離を詰めればケイルは逃げられない。"},
            {"name": "Jax", "reason": "EでAAを無効化し、Qで飛びつける。"},
        ]
    }
    # 必要に応じてここに追加
}

# -----------------------------------------------------------
# 1. データ取得
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
            id_map[display_name] = {'id': key, 'key': val['key']}
        return version, sorted(champ_list), id_map
    except:
        return None, [], {}

# -----------------------------------------------------------
# 2. メイン画面のスタイル設定 (横並び・コンパクト化)
# -----------------------------------------------------------
st.set_page_config(page_title="LOL.GG", page_icon="⚔️", layout="wide")

st.markdown("""
    <style>
    /* 全体 */
    .stApp { background-color: #0f0f0f; color: #e0e0e0; }
    h1 { font-family: 'Segoe UI', sans-serif; color: #c8aa6e; font-size: 2.5rem !important; text-align: center; margin: 0; padding: 0; }
    
    /* 検索バーをコンパクトに */
    .search-container { background-color: #1e1e1e; padding: 10px; border-radius: 8px; border: 1px solid #444; margin-bottom: 10px; }
    
    /* 画像と情報の横並びレイアウト調整 */
    .hero-img { width: 100%; border-radius: 8px; border: 1px solid #444; }
    
    /* スキルカード (コンパクト) */
    .skill-box { background: #1a1a1a; border: 1px solid #333; padding: 5px; border-radius: 4px; text-align: center; margin-bottom: 5px; }
    .skill-key { color: #c8aa6e; font-weight: bold; font-size: 0.9rem; }
    .skill-val { color: #fff; font-weight: bold; font-size: 1rem; }
    
    /* 対策BOX (コンパクト) */
    .tips-container { background-color: #222; padding: 10px; border-radius: 6px; border-left: 4px solid #ff4c4c; height: 100%; font-size: 0.9rem; }
    .tips-header { color: #ff4c4c; font-weight: bold; margin-bottom: 5px; }
    
    /* カウンターリスト */
    .counter-row { display: flex; gap: 10px; margin-top: 5px; }
    .counter-item { background: #333; padding: 5px 10px; border-radius: 4px; border: 1px solid #555; font-size: 0.85rem; flex: 1; }
    
    /* ボタン */
    div.stButton > button { width: 100%; padding: 0.3rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------
# 3. メイン処理
# -----------------------------------------------------------
def main():
    st.markdown("<h1>LOL.GG</h1>", unsafe_allow_html=True)
    version, champ_list, id_map = load_data()
    if not version: return

    # === 検索エリア ===
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            my_choice = st.selectbox("🔵 自分", champ_list, index=None, placeholder="Select Your Champ...", label_visibility="collapsed")
        with c2:
            enemy_choice = st.selectbox("🔴 相手", champ_list, index=None, placeholder="Select Enemy Champ...", label_visibility="collapsed")

    # === データ表示エリア (横並びレイアウト) ===
    if enemy_choice:
        enemy_data = id_map[enemy_choice]
        champ_id = enemy_data['id']
        
        # Riot APIデータ取得
        detail_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ja_JP/champion/{champ_id}.json"
        try:
            res = requests.get(detail_url).json()['data'][champ_id]
            spells = res['spells']
        except: return

        st.divider()
        
        # ★ここが新レイアウト (左：画像 / 右：情報)
        col_left, col_right = st.columns([1, 2]) # 1:2の比率
        
        # --- 左カラム：画像 ---
        with col_left:
            splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_id}_0.jpg"
            st.image(splash_url, use_container_width=True)
            
            # 外部リンクボタン
            url_enemy = "wukong" if champ_id == "MonkeyKing" else champ_id.lower()
            st.link_button("📉 U.GG (カウンター)", f"https://u.gg/lol/champions/{url_enemy}/counter", use_container_width=True)
            st.link_button("🇰🇷 LOL.PS", f"https://lol.ps/champ/{enemy_data['key']}/statistics/", use_container_width=True)

        # --- 右カラム：CD＆秘伝メモ ---
        with col_right:
            # 1. スキルCD (横並び)
            c_q, c_w, c_e, c_r = st.columns(4)
            keys = ['Q', 'W', 'E', 'R']
            for i, col in enumerate([c_q, c_w, c_e, c_r]):
                cd = "/".join(map(str, spells[i]['cooldown']))
                col.markdown(f"<div class='skill-box'><span class='skill-key'>{keys[i]}</span><br><span class='skill-val'>{cd}</span></div>", unsafe_allow_html=True)
            
            # 2. 秘伝の攻略メモ (あれば表示)
            if champ_id in CUSTOM_DATA:
                cust = CUSTOM_DATA[champ_id]
                
                # 危険なアクション & Tips
                tips_html = ""
                if "danger" in cust:
                    tips_html += f"<div style='color:#ff4c4c; font-weight:bold;'>⚠ 危険なアクション</div><ul>"
                    for d in cust['danger']: tips_html += f"<li>{d}</li>"
                    tips_html += "</ul>"
                
                if "tips" in cust:
                    tips_html += f"<div style='color:#0ac8b9; font-weight:bold; margin-top:10px;'>💡 意識すること</div><ul>"
                    for t in cust['tips']: tips_html += f"<li>{t}</li>"
                    tips_html += "</ul>"
                
                if tips_html:
                    st.markdown(f"<div class='tips-container'>{tips_html}</div>", unsafe_allow_html=True)

                # カウンター情報
                if "counters" in cust:
                    st.markdown("##### 🛡️ 有利ピック & 理由")
                    for c in cust['counters']:
                        st.info(f"**VS {c['name']}**: {c['reason']}")

            else:
                st.info("※ このチャンピオンのカスタム攻略メモはまだありません。")

    # === 自分のキャラ用リンク (OTP Ranking) ===
    if my_choice:
        my_data = id_map[my_choice]
        my_url = "wukong" if my_data['id'] == "MonkeyKing" else my_data['id'].lower()
        
        st.success(f"🔵 **{my_choice}** 選択中")
        c1, c2 = st.columns(2)
        with c1:
            # DeepLoL OTP Ranking (Mastery)
            st.link_button("🔥 DeepLoL (OTP Ranking)", f"https://www.deeplol.gg/champions/{my_url}/mastery", use_container_width=True)
        with c2:
            st.link_button("📈 U.GG (Build)", f"https://u.gg/lol/champions/{my_url}/build", use_container_width=True)

if __name__ == "__main__":
    main()
