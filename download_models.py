import os
import urllib.request

# Create 'models' folder if it doesn't exist
if not os.path.exists("models"):
    os.makedirs("models")

print("⬇️ Downloading Gender Model Files from Alternate Source...")

# We use a User-Agent header because GitHub sometimes blocks Python scripts
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
urllib.request.install_opener(opener)

# NEW STABLE LINKS
url_proto = "https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/gender_deploy.prototxt"
url_model = "https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/gender_net.caffemodel"

try:
    print("⏳ Downloading Structure file (prototxt)...")
    urllib.request.urlretrieve(url_proto, "models/gender_deploy.prototxt")
    print("✅ gender_deploy.prototxt downloaded!")

    print("⏳ Downloading Weight file (caffemodel) - This is 45MB, please wait...")
    urllib.request.urlretrieve(url_model, "models/gender_net.caffemodel")
    print("✅ gender_net.caffemodel downloaded!")

    print("\n🎉 SUCCESS! You can now run 'python main.py'")

except Exception as e:
    print(f"\n❌ Error downloading: {e}")
    print("Try downloading manually if this fails again.")