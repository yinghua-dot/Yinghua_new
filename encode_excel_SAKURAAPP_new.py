import base64

with open ("Yinghua_Player_list.xlsx","rb") as f:
    encoded=base64.b64encode(f.read()).decode("utf-8")

with open("encoded.txt","w") as f:
    f.write(encoded)