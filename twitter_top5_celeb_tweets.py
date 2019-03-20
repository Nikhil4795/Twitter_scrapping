import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from lxml import html
from time import sleep
from random import randint
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import datetime

range_date = '1 Jan 2019'

dataout = open("my_results_new.csv","wb")
datawrite = csv.writer(dataout)
header = ["Name", "No. of tweets active", "Following", "Followers", \
          "Tweet date", "Tweet Time", "Tweet ID", "Tweet Content",\
          "Hashtags", "Tagged People", "Comments", "Retweet", "Like"]
datawrite.writerow(header)

def removeNonAscii(s):
    return "".join(filter(lambda x: ord(x)<128, s))

def clean_text(input_given):
    temp_list = []
    for i in range(0,len(input_given)):
        temp = input_given[i]
        temp = temp.replace("\n"," ").replace("\t"," ")
        while("  " in temp):
            temp = temp.replace("  "," ")
        temp = temp.strip()
        if len(temp) > 0:
            temp = removeNonAscii(temp)

        if len(temp) > 0:
            temp_list.append(temp)
    return temp_list

def crl(input_given):
    input_given = clean_text(input_given)
    temp_list = []
    for il in range(0,len(input_given)):
        if "like" in input_given[il].lower() or \
           "reply" in input_given[il].lower()or \
           "retweet" in input_given[il].lower() or \
           "tweet" in input_given[il].lower() or \
           "follow" in input_given[il].lower():
            pass
        else:
            if input_given[il] in temp_list:
                pass
            else:
                temp_list.append(input_given[il])

    return " | ".join(temp_list)


def hashtags_finder(input_given):
    temp_list = []
    temp_list_1 = []
    for il in range(0,len(input_given)):
        if input_given[il].startswith("#"):
            if input_given[il] in temp_list:
                pass
            else:
                temp_list.append(input_given[il+1])

        if input_given[il].startswith("@"):
            if input_given[il] in temp_list_1:
                pass
            else:
                temp_list_1.append(input_given[il+1])

    return " | ".join(temp_list), " | ".join(temp_list_1)
        
        

def month_number(input_given):
    if input_given == 'Jan':
        return "01"
    elif input_given == 'Feb':
        return "02"
    elif input_given == 'Mar':
        return "03"
    elif input_given == 'Apr':
        return "04"
    elif input_given == 'May':
        return "05"
    elif input_given == 'Jun':
        return "06"
    elif input_given == 'Jul':
        return "07"
    elif input_given == 'Aug':
        return "08"
    elif input_given == 'Sep':
        return "09"
    elif input_given == 'Oct':
        return "10"
    elif input_given == 'Nov':
        return "11"
    elif input_given == 'Dec':
        return "12"
    else:
        return input_given

def date_time_seperator(input_given):
    date = ""
    time = ""
    temp = input_given[0]
    index = temp.index('-')
    time = temp[:index]
    date = temp[index + 1 : ]
    date = date.strip()
    time = time.strip()
    return date,time

def date_modifier(input_given):
    input_list = input_given.split(" ")
    for il in range(0,len(input_list)):
        input_list[il] = input_list[il].strip()
        input_list[il] = month_number(input_list[il])
    return "-".join(input_list)



def range_selected(input_given, input_given_1):
    #input_given   = tweet date
    #input_given_1 = range_date
    input_given = date_modifier(input_given)
    input_given_1 = date_modifier(input_given_1)
    input_given = datetime.datetime.strptime(input_given,"%d-%m-%Y").strftime("%Y-%m-%d")
    input_given_1 = datetime.datetime.strptime(input_given_1,"%d-%m-%Y").strftime("%Y-%m-%d")

    if input_given >= input_given_1:
        return "yes"
    else:
        return "no"

driver = webdriver.Firefox()

celeb_list=["@katyperry", "@justinbieber", "@BarackObama",\
            "@rihanna", "@taylorswift13"]

for cl in range(0,len(celeb_list)):
    print(celeb_list[cl])
    url = "https://twitter.com/"+str(celeb_list[cl])+""
    driver.get(url)
    sleep(randint(5,8))
    i = 1
    while(i > 0):
        try:
            row_data = []
            HTMLTree = html.fromstring(driver.page_source)
            profile_name = HTMLTree.xpath('//a[@class="ProfileHeaderCard-nameLink u-textInheritColor js-nav"]//text()')
            row_data.append(" | ".join(profile_name))

            tweets_active = HTMLTree.xpath('//li[@class="ProfileNav-item ProfileNav-item--tweets is-active"]//text()')
            tweets_active = crl(tweets_active)
            row_data.append(tweets_active)

            following_count = HTMLTree.xpath('//li[@class="ProfileNav-item ProfileNav-item--following"]//text()')
            following_count = crl(following_count)
            row_data.append(following_count)

            followers_count = HTMLTree.xpath('//li[@class="ProfileNav-item ProfileNav-item--followers"]//text()')
            followers_count = crl(followers_count)
            row_data.append(followers_count)
            
            time_and_date = HTMLTree.xpath('//ol[@id="stream-items-id"]\
                                        //li[@data-item-type="tweet"]['+str(i)+']\
                                        //div[@class="stream-item-header"]\
                                        //small[@class="time"]//a//@title')

            final_data = clean_text(time_and_date)

            final_date, final_time = date_time_seperator(final_data)

            result = range_selected(final_date, range_date)
            if result == "yes":
                row_data.append(final_date)
                row_data.append(final_time)
                
                tweet_id = HTMLTree.xpath('//ol[@id="stream-items-id"]\
                                            //li[@data-item-type="tweet"]['+str(i)+']\
                                            //@data-tweet-id')

                row_data.append(("#"+(str(tweet_id[0]))))


                tweet_content = HTMLTree.xpath('//ol[@id="stream-items-id"]\
                                            //li[@data-item-type="tweet"]['+str(i)+']\
                                            //div[@class="js-tweet-text-container"]\
                                            //text()')

                tweet_content = clean_text(tweet_content)

                row_data.append(" | ".join(tweet_content))

                hashtags, tagged_ppl = hashtags_finder(tweet_content)

                row_data.append(hashtags)
                row_data.append(tagged_ppl)

                tweet_comments = HTMLTree.xpath('//ol[@id="stream-items-id"]\
                                            //li[@data-item-type="tweet"]['+str(i)+']\
                                            //div[@class="stream-item-footer"]\
                                            //div[@class="ProfileTweet-action ProfileTweet-action--reply"]\
                                            //text()')

                tweet_comments = crl(tweet_comments)
                row_data.append(tweet_comments)

                tweet_retweet = HTMLTree.xpath('//ol[@id="stream-items-id"]\
                                            //li[@data-item-type="tweet"]['+str(i)+']\
                                            //div[@class="stream-item-footer"]\
                                            //div[@class="ProfileTweet-action ProfileTweet-action--retweet js-toggleState js-toggleRt"]\
                                            //text()')

                tweet_retweet = crl(tweet_retweet)
                row_data.append(tweet_retweet)

                tweet_like = HTMLTree.xpath('//ol[@id="stream-items-id"]\
                                            //li[@data-item-type="tweet"]['+str(i)+']\
                                            //div[@class="stream-item-footer"]\
                                            //div[@class="ProfileTweet-action ProfileTweet-action--favorite js-toggleState"]\
                                            //text()')

                tweet_like = crl(tweet_like)
                row_data.append(tweet_like)

                datawrite.writerow(row_data)
                i = i+1
            else:
                break
        except:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(randint(8,10))

dataout.close()
print("Over")




