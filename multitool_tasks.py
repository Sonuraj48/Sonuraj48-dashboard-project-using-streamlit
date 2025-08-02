import psutil
import datetime
import pywhatkit as kit
import os
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
from serpapi import GoogleSearch
import requests
import sys
import timeit
import cv2
import numpy as np
import mediapipe as mp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
from PIL import Image
import json

load_dotenv()

def monitor_ram():
    mem = psutil.virtual_memory()
    return f"Used RAM: {mem.used / (1024 ** 3):.2f} GB | Usage: {mem.percent}%"

def send_whatsapp_message_pywhatkit(phone_number, message):
    now = datetime.datetime.now()
    send_hour = now.hour
    send_minute = now.minute + 1
    try:
        kit.sendwhatmsg(phone_number, message, send_hour, send_minute)
        return "📤 Message scheduled successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

def send_email_gmail(to_email, subject, body):
    try:
        from_email = os.getenv("EMAIL_ADDRESS")
        app_password = os.getenv("EMAIL_APP_PASSWORD")
        if not from_email or not app_password:
            return "❌ Missing email credentials."
        msg = EmailMessage()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

def send_whatsapp_twilio(to_number, message):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
        msg = client.messages.create(body=message, from_=from_whatsapp, to=f"whatsapp:{to_number}")
        return f"✅ Message sent via Twilio! SID: {msg.sid}"
    except Exception as e:
        return f"❌ Error: {e}"

def send_sms(to_number, message):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        msg = client.messages.create(body=message, from_=os.getenv("TWILIO_PHONE_NUMBER"), to=to_number)
        return f"✅ SMS sent! SID: {msg.sid}"
    except Exception as e:
        return f"❌ Error: {e}"

def make_call(to_number):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        call = client.calls.create(to=to_number, from_=os.getenv("TWILIO_PHONE_NUMBER"), url="http://demo.twilio.com/docs/voice.xml")
        return f"📞 Call initiated! Call SID: {call.sid}"
    except Exception as e:
        return f"❌ Error: {e}"

# def google_search(query, num_results=5):
#     try:
#         search = GoogleSearch({
#             "engine": "google",
#             "q": query,
#             "num": num_results,
#             "api_key": os.getenv("SERPAPI_API_KEY")
#         })
#         results = search.get_dict().get("organic_results", [])
#         return "\n\n".join([f"{i+1}. {r['title']}\n🔗 {r['link']}\n📝 {r.get('snippet', '')}" for i, r in enumerate(results)])
#     except Exception as e:
#         return f"❌ Error: {e}"




def google_search(query, num_results=5):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return [{"title": "API Key Required", "link": "", "snippet": "Please set SERPAPI_API_KEY in your .env file"}]

    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "organic_results" in results:
            output = []
            for i, res in enumerate(results["organic_results"], 1):
                title = res.get("title", "No title")
                link = res.get("link", "")
                snippet = res.get("snippet", "No description available")
                output.append({"title": title, "link": link, "snippet": snippet})
            return output
        else:
            return [{"title": "No Results", "link": "", "snippet": "No search results found"}]

    except Exception as e:
        return [{"title": "Error", "link": "", "snippet": f"Search error: {str(e)}"}]


def download_basic_website(url, output_dir="website"):
    os.makedirs(output_dir, exist_ok=True)
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        return f"✅ Website HTML saved in {output_dir}/index.html"
    except Exception as e:
        return f"❌ Error: {e}"

def send_anonymous_email(to_email, subject, body):
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{os.getenv('MAILGUN_DOMAIN')}/messages",
            auth=("api", os.getenv("MAILGUN_API_KEY")),
            data={
                "from": f"Mailgun Sandbox <postmaster@{os.getenv('MAILGUN_DOMAIN')}>",
                "to": [to_email],
                "subject": subject,
                "text": body
            }
        )
        if response.status_code == 200:
            return "✅ Email sent anonymously!"
        return f"❌ Failed. Status: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {e}"

def list_vs_tuple_comparison():
    try:
        my_list = [1, 2, 3]
        my_tuple = (1, 2, 3)
        result = []
        result.append("✅ List is mutable:")
        my_list[0] = 100
        result.append(f"Modified List: {my_list}")
        result.append("\n❌ Tuple is immutable:")
        try:
            my_tuple[0] = 100
        except TypeError as e:
            result.append(f"Error: {e}")
        result.append(f"\n📌 List methods: {[m for m in dir(my_list) if not m.startswith('__')][:5]}")
        result.append(f"📌 Tuple methods: {[m for m in dir(my_tuple) if not m.startswith('__')][:5]}")
        result.append(f"\n💾 Memory size List: {sys.getsizeof(my_list)} bytes")
        result.append(f"💾 Memory size Tuple: {sys.getsizeof(my_tuple)} bytes")
        
        # Use smaller number for performance test to avoid long execution
        list_time = timeit.timeit(stmt="[1,2,3,4,5]", number=100000)
        tuple_time = timeit.timeit(stmt="(1,2,3,4,5)", number=100000)
        result.append(f"\n⚡ List creation time: {round(list_time, 6)}s")
        result.append(f"⚡ Tuple creation time: {round(tuple_time, 6)}s")
        return "\n".join(result)
    except Exception as e:
        return f"❌ Error in comparison: {str(e)}"

def capture_image():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            return "❌ Could not open camera. Please check if camera is available."
            
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return "❌ Could not capture image from camera."
            
        cv2.imwrite("digital_image.jpg", frame)
        cap.release()
        return "📸 Image saved as digital_image.jpg"
    except Exception as e:
        return f"❌ Error capturing image: {str(e)}"

def swap_faces(img1, img2):
    try:
        mp_face_mesh = mp.solutions.face_mesh
        def get_landmarks(image):
            try:
                with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                            refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
                    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    if not results.multi_face_landmarks:
                        return None
                    h, w, _ = image.shape
                    return np.array([[p.x * w, p.y * h] for p in results.multi_face_landmarks[0].landmark], dtype=np.float32)
            except Exception as e:
                print(f"Error getting landmarks: {e}")
                return None
                
        def warp_triangle(src, dst, t_src, t_dst):
            try:
                r1 = cv2.boundingRect(np.float32([t_src]))
                r2 = cv2.boundingRect(np.float32([t_dst]))
                t1_rect = [(p[0]-r1[0], p[1]-r1[1]) for p in t_src]
                t2_rect = [(p[0]-r2[0], p[1]-r2[1]) for p in t_dst]
                mat = cv2.getAffineTransform(np.float32(t1_rect), np.float32(t2_rect))
                src_crop = src[r1[1]:r1[1]+r1[3], r1[0]:r1[0]+r1[2]]
                warped = cv2.warpAffine(src_crop, mat, (r2[2], r2[3]), borderMode=cv2.BORDER_REFLECT_101)
                mask = np.zeros((r2[3], r2[2], 3), dtype=np.uint8)
                cv2.fillConvexPoly(mask, np.int32(t2_rect), (1,1,1))
                dst_crop = dst[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]]
                dst[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = dst_crop * (1 - mask) + warped * mask
                return dst
            except Exception as e:
                print(f"Error in warp_triangle: {e}")
                return dst
                
        # Validate input images
        if img1 is None or img2 is None:
            return "❌ Invalid input images.", None
            
        if len(img1.shape) != 3 or len(img2.shape) != 3:
            return "❌ Images must be 3-dimensional (BGR).", None
            
        landmarks1 = get_landmarks(img1)
        landmarks2 = get_landmarks(img2)
        
        if landmarks1 is None or landmarks2 is None:
            return "❌ Could not detect faces in one or both images.", None
            
        output = img2.copy()
        
        # Limit the number of landmarks to process to avoid errors
        max_landmarks = min(len(landmarks1), len(landmarks2), 100)
        
        for i in range(max_landmarks):
            try:
                warp_triangle(img1, output, [landmarks1[i]]*3, [landmarks2[i]]*3)
            except Exception as e:
                print(f"Error processing landmark {i}: {e}")
                continue
                
        output_path = "swapped_face.jpg"
        cv2.imwrite(output_path, output)
        return "✅ Face swapped successfully!", output_path
        
    except Exception as e:
        return f"❌ Face swap failed: {str(e)}", None
