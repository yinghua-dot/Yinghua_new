import streamlit as st # type: ignore
import pandas as pd
import io
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import smtplib
from email.message import EmailMessage

# SecretsからExcelを復元、読み込み
excel_bytes = base64.b64decode(st.secrets["EXCEL_BASE64"])

excel_io = io.BytesIO(excel_bytes)
df = pd.read_excel(excel_io)

# メンバー辞書
allmenber = dict(zip(df["Name"], df["Player_No"]))
staff_list = {name for name, num in allmenber.items() if isinstance(num, str) and not pd.isna(num)}
player_list = {name: num for name, num in allmenber.items() if isinstance(num, (int,float)) and not pd.isna(num)}
player_multiselect_list = [f"No,{num} {name}" for name, num in player_list.items()]


#メール送信関数
def send_email_with_image(image_path):
    from_email = st.secrets["EMAIL_USER"]
    app_password = st.secrets["EMAIL_PASS"]
    to_email = st.secrets["EMAIL_TO"]

    msg = EmailMessage()
    msg["Subject"] = "Starting11"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content("Starting 11IMG")

    with open(image_path, "rb") as f:
        img_data = f.read()
        msg.add_attachment(img_data, maintype="image", subtype="png", filename=image_path)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, app_password)
        server.send_message(msg)
    

#本体(Streamlit画面)
st.title("hello SAKURA")
st.write("made by me")

# セッション状態の初期化
if "selected" not in st.session_state:
    st.session_state["selected"] = []

if "confirmed" not in st.session_state:
    st.session_state["comfirmed"]=False

#確認画面
if st.session_state.get("confirmed", False):
    st.header("確認画面")

    #メンバー再取得＆整形（表示用）
    selected_menber={}
    for item in st.session_state.selected:
        name=item.split(" ")[1]
        number=allmenber.get(name)
        if number is not None:
            selected_menber[name]=number
    selected_menber=dict(sorted(selected_menber.items(), key=lambda item:item[1]))

    st.subheader(f"Staff {staff_list}")
    st.subheader("Selected 11")
    for name,number in selected_menber.items():
        st.write(f"- {name} (No,{number})")
    
    if st.button("Agein"):
        st.session_state.confirmed=False
    
    if st.button("OK"):
        
        try:
            #Pillowで画像生成
            template_path="Starting_XI.png" # Canvaで作った背景画像
            output_path = f"MATCHDAY_{datetime.now().strftime('%Y%m%d')}.png"
            template = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(template)
            # フォント設定
            FONT_PATH = os.path.join("fonts", "NotoSansTC-SemiBold.ttf")
            font = ImageFont.truetype(FONT_PATH, 50)

            # 番号描画
            y_start = 408
            x_number = 253
            line_height = 67
            for idx, (name, number) in enumerate(selected_menber.items()):
                y_pos = y_start + idx*line_height
                draw.text((x_number, y_pos), f" {number}", font=font, fill="#f0edf0")

            # 名前描画
            y_start=408
            x_name = 337
            line_height=67
            for idx, (name, number) in enumerate(selected_menber.items()):
                y_pos = y_start + idx*line_height
                draw.text((x_name, y_pos), f" {name}", font=font, fill="#f0edf0")
            
            template.save(output_path)
            st.image(output_path, caption="Starting11IMG", use_container_width=True)
            st.success(f"Complete 画像生成完了: {output_path}")

            #メール送信を追加
            send_email_with_image(output_path)
            st.success("メール送信完了")

        except Exception as e:
            st.error(f"Error:{e}")
    

    
#選択画面（未確定）
else:
    col1,col2=st.columns([1,1])
    with col1:
        select=st.multiselect("Select menber(max11)",options=player_multiselect_list,default=st.session_state.selected, key="multiselect")
    with col2:
        st.markdown("###")
        st.markdown(f"##{len(select)}/11")

        #エラーチェック
        if len(select)>11:
            st.error("⚠️ Already 11")
        elif len(select)==11:
            st.success("Complete")  
        else:
            st.info(f"{len(select)}/11 selected")
    
    selected_raw=st.session_state.selected if st.session_state.get("confirmed", False) else select
    #メンバー辞書に変換
    selected_menber={}
    for item in selected_raw:
        name=item.split(" ")[1]
        number=allmenber.get(name)
        if number is not None:
            selected_menber[name]=number

    selected_menber=dict(sorted(selected_menber.items(), key=lambda item:item[1]))    

    st.write("Menber")
    for name,number in selected_menber.items():
        st.write(f"- {name} (No,{number})")

    #OKボタン処理（11人なら画面切替
    if st.button("Sent"):
        if len(selected_raw)==11:
            st.session_state.selected=select
            st.session_state.confirmed=True
        else:
            st.warning("⚠️ Please select exactly 11 members") 
