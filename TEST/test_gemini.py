import google.generativeai as genai

genai.configure(api_key="")  # ← 실제 API 키 입력

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

response = model.generate_content("나 요즘 우울해")
print(response.text)
