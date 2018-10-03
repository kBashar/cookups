from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from openpyxl import Workbook

import re

'''username of the poster is in a div having class name "fwb"'''
def get_username(post):
    name = post.find(class_="fwb").text
    return name

''' post title is in a div having class "_l53". \
        this should be mentioned this machine generated name may change anytim\
        so to make it work a constant vigilance is required'''
def get_title(post):
    title = post.find(class_="_l53")
    if title is not None:
        return title.text

''' price of the recipe is in a div of "_l57" class and this also requires vigilance as title extraction'''
def get_price(post):
    price = post.find(class_="_l57")
    if price is not None:
        return price.text[1:]

''' location of the cook is in "_l57" class'''
def get_location(post):
    location = post.find(class_="_l58")
    if location is  not None:
        return location.text

''' time of an element is inside an abbr tag and time is given in title attribute'''
def get_time(post):
    elm = post.find("abbr")
    return elm.get("title")

''' description is in a div which has a class "text_exposed_root"'''
def get_description(post):
    description = []
    discards = ['...', 'see more']
    description_elm = post.find_all(class_="userContent")[1]
    description_elm = description_elm.find_all("p")
    for des in description_elm:
        text = des.text
        if text not in discards:
            description.append(des.text)
    return "".join(description)

''' link to cookupa webite is in the description, a regex search is used to find the urls'''
def get_urls(post):
    description_text = post.find_all(class_="userContent")[1].text
    urls = re.findall(r'https://cookups.com.bd/offers/\d{5}', description_text)
    return urls

''' parse image url data'''
def get_image_url(post):
    img_src = post.find_all("img")[1].get("src")
    id = re.findall(r'[a-z\d\-]{36}.jpg', img_src)[0]
    url = "https://cookupsapp.s3.amazonaws.com/media/" + id
    return url

'''save data in a xl file'''
def save_in_xl(post_list):
    wb = Workbook()
    ws = wb.active
    ws.append(("Cook", "Time", "Title", "Location", "Price", "Description", "Order link", "Image Url"))
    for post in post_list:
        ws.append(post)

    wb.save("cookups_posts.xlsx")

''' save data in a file in json format'''
def save_in_file(post_list):
    import json
    f = open("data.json", "w")
    f.write(json.dumps(post_list))
    f.close()

''' login to facebook'''
def login(driver):
    ''' open facebook login page, as without login facebook doesn't permit browsing closed groups'''
    driver.get("https://www.facebook.com/login")

    ''' to log in input your credentials'''
    email=input("enter user id: ")
    passward=input("enter Passward: ") 
    
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("pass").send_keys(passward)
    driver.find_element_by_id("loginbutton").click()

'''extract data from each user posts'''
def extract_data(posts):
    post_data = []
    post_xl_data = []
    for post in posts:
        username = get_username(post)
        if (username != 'Cookups') and (username != 'CookupsFit'):
            print("{0} is fetching".format(username))
            time = get_time(post)
            title = get_title(post)
            price = get_price(post)
            location = get_location(post)
            description = get_description(post)
            urls = get_urls(post)
            image = get_image_url(post)
            
            xl_data = (username, time, title, location, price, description, str(urls), image)
            data = {
                'name': username,
                'time': time,
                'title': title,
                'price': price,
                'location': location,
                'description': description,
                'urls': urls,
                'image': image
                }
            post_data.append(data)
            post_xl_data.append(xl_data)
            print("{0} posted at {1}".format(username, time))

    return(post_data, post_xl_data)

def main():
    '''initiate webdriver. this will open a firfox instance'''
    driver = webdriver.Firefox()
    login(driver)

    ''' open cookups facebook group'''
    driver.get("https://www.facebook.com/groups/cookupsBD")

    '''populate beautifulsoup with page html source'''
    html_soup = BeautifulSoup(driver.page_source, "html.parser")

    ''' fetch user posts feed which are inside a div having class "userContentWrapper" '''
    posts = html_soup.find_all(class_="userContentWrapper")

    print("Total number of posts found is {0}".format(len(posts)))

    data_tuple = extract_data(posts)
    save_in_file(data_tuple[0])
    save_in_xl(data_tuple[1])

if __name__== "__main__":
    main()
