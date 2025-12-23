import google.generativeai as genai
import os

MY_API_KEY = "AIzaSyCIMS5ZXzek-RWI38Cp0M5sezcV2ltOWLA"
if not MY_API_KEY:
    print("Lỗi: Chưa có API Key.")
else:
    try:
        genai.configure(api_key=MY_API_KEY)

        model = genai.GenerativeModel('gemini-2.5-flash')

        print("Đang gửi yêu cầu tới Gemini...")
        
        response = model.generate_content("giới hạn token của gemini-2.5-flash là bao nhiêu? khi sử dung api key free")

        print("\n KẾT QUẢ TEST THÀNH CÔNG:")
        print(response.text)

    except Exception as e:
        print("\nTEST THẤT BẠI:")
        print(e)