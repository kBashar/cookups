from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

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
    description_elm = post.find(class_="userContent").find_all("p")
    for des in description_elm:
        text = des.text
        if text not in discards:
            description.append(des.text)
    return "".join(description)

''' link to cookupa webite is in the description, a regex search is used to find the urls'''
def get_urls(post):
    description_text = post.find(class_="userContent").text
    urls = re.findall(r'https://cookups.com.bd/offers/\d{5}', description_text)
    return urls

''' parse image url data'''
def get_image_url(post):
    img_src = post.find_all("img")[1].get("src")
    id = re.findall(r'[a-z\d\-]{36}.jpg', img_src)[0]
    url = "https://cookupsapp.s3.amazonaws.com/media/" + id
    return url


'''initiate webdriver. this will open a firfox instance'''
driver = webdriver.Firefox()

''' open facebook login page, as without login facebook doesn't permit browsing closed groups'''
driver.get("https://www.facebook.com/login")

''' to log in input your credentials'''
driver.find_element_by_id("email").send_keys("kbashar.0.1")
driver.find_element_by_id("pass").send_keys("rflbodn@2020")
driver.find_element_by_id("loginbutton").click()


''' open cookups facebook group'''
driver.get("https://www.facebook.com/groups/cookupsBD")

'''populate beautifulsoup with page html source'''
html_soup = BeautifulSoup(driver.page_source, "html.parser")

''' fetch user posts feed which are inside a div having class "userContentWrapper" '''
posts = html_soup.find_all(class_="userContentWrapper")

print("Total number of posts found is {0}".format(len(posts)))

post_data = []
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
        print("{0} posted at {1}".format(username, time))

f = open("data.txt", "w")
f.write(str(post_data))
f.close()

