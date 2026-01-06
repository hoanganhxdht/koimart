import os
import urllib.request

def download_font(url, filename):
    folder = os.path.join('app', 'static', 'fonts')
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    path = os.path.join(folder, filename)
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"Success: {path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_font("https://raw.githubusercontent.com/google/fonts/master/apache/roboto/Roboto-Regular.ttf", "Roboto-Regular.ttf")
    download_font("https://raw.githubusercontent.com/google/fonts/master/apache/roboto/Roboto-Bold.ttf", "Roboto-Bold.ttf")
