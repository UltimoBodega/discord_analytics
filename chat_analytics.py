from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import defaultdict 

show_top = 30
filename = 'chat.html'

with open(filename, 'r', encoding="utf8") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, 'lxml')
    chatlog = soup.find_all('div', class_='chatlog__messages')
    char_count = defaultdict(int)
    word_dict = defaultdict(int)
    word_counter = defaultdict(int)
    for i in range(len(chatlog)):
        person = chatlog[i].find_all('span', class_='chatlog__author-name')[0].get_text()
        for message in chatlog[i].find_all('span', class_='preserve-whitespace'):
            char_count[person] = char_count[person] + len(message.get_text())
            word_dict[person] = word_dict[person] + len(message.get_text().split())
            for w in message.get_text().split():
                word_counter[w] += 1

    plt.bar(char_count.keys(), char_count.values(), color='g',label='Character count')
    plt.bar(word_dict.keys(), word_dict.values(), color='r',label='Word count')
    plt.xlabel("Players")
    plt.grid()
    plt.legend()
    
    popular_words = sorted(word_counter, key = word_counter.get, reverse = True)
    tops = popular_words[:show_top]
    for p, count in sorted(char_count.items(), key=lambda item: item[1], reverse=True):
        print(f"El {p}: {count}")
    for i in range(len(tops)):
        print(f"#{i}: {tops[i]}, ocurrances: {word_counter[tops[i]]}")

    plt.show()