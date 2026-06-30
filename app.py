from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import os

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
                try:

                    # query to search for images
                    query = request.form['content'].replace(" ","")
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
                    driver.get(f"https://www.bing.com/images/search?q={query}")
                   
                    #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))
                    time.sleep(5) # Give Google Images time to load after CAPTCHA
                    images = driver.find_elements(By.CSS_SELECTOR, "img.mimg")
                    
                    print("Total images found:", len(images))
                    save_directory = "images"
                    if not os.path.exists(save_directory):
                          os.makedirs(save_directory)
                    #return f"Found {len(images)} images"
                    img_data = []

                    count = 0
                    for image in images:
                           try:
                                   src = image.get_attribute("src")
                                   print(src)
                                   if src and src.startswith("http"):
                                           image_data = requests.get(src).content
                                           print(os.path.join(save_directory, f"{query}_{count}.jpg"))
                                           with open(os.path.join(save_directory, f"{query}_{count}.jpg"), "wb") as f:
                                                   f.write(image_data)
                                                   img_data.append({
                "Index": count,
                "Image": src
            })
                                                   count += 1
                                                   if count == 20:
                                                           break
                           except Exception as e:
                                                   print(e)
                                                   driver.quit()
                                                   return f"{count} images downloaded successfully!"
                    

                          
                    client = pymongo.MongoClient("mongodb+srv://iqrakhan78786_db_user:iqramongopass@cluster1.3joayct.mongodb.net/?appName=Cluster1")
                    db = client['image_scrap']
                    review_col = db['image_scrap_data']
                    review_col.insert_many(img_data)          

                    return "image laoded"
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return str(e)
            # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
