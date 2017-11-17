import os
import argparse
from bs4 import BeautifulSoup
import csv
import json
import requests
from pprint import pprint
import wikipedia
import re

from threading import Thread, Lock
from queue import Queue

concurrent = 16
q = Queue(concurrent *2)

corpus_lock = Lock()

def fetch_html_page(fout):

    while True:
        url = q.get()

        # Fetch HTTP requests
        req = requests.get(url)

        # Check status code
        if not req.status_code == requests.codes.ok:
            print('Return status', req.status_code)
            continue

        # Parse the html files
        soup = BeautifulSoup(req.text, 'html.parser')

        # Extract all the text in p tags
        val = soup.find_all('p')
        txt = []

        for i in range(0, len(val)):

            # Remove the references
            txt.append(re.sub(r'\[[0-9]+\]', '', val[i].text))

            # Check if the content is enough to segregate into summary and content
            if(len(txt) < 2):
                print("Not enough content")
                continue

            summary = txt[0]
            content = ' '.join([x for x in txt[1:]])

            # Data samples will be written in the form of <start> Summary "---->" Content <stop>
            out = "<start>" + summary + "---->" + content + "<stop>\n"

            # Acquire a lock as multiple thread could access the same file
            corpus_lock.acquire()

            # Write to the file with utf-8 encoding
            fout.write(out.encode('utf-8'))

            # Release the lock
            corpus_lock.release()
            print("Written to corpus file ...  ")

        # Mark the task done
        q.task_done()


def extract_urls(args):
    for root, subdirs, files in os.walk(args.input_dir):
        for f in files:
            # if file starts with wiki_ as per WikiExtractor
            if not f.startswith('wiki_'):
                print("Invalid file found")
                continue

            list_file_path = os.path.join(root, f)
            print('Processing file = ' + list_file_path)
            with open(list_file_path, 'r') as fin:
                for line in fin.readlines():
                    try:
                        dump = json.loads(line)
                    except:
                        print("Json parsing invalid format. Skipping")
                        continue
                    topic = dump['title']

                    # Remove all the spaces with underscore for HTTP requests
                    topic = topic.replace(" ", "_")
                    print('Processing article', topic)

                    # Enqueue URL into the queue
                    q.put(wikipedia_url + topic)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, help='Input dump path')
    parser.add_argument('--output_file', type=str, help='Output file for dumping the wikipedia content')

    args = parser.parse_args()

    wiki_prefix = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids="
    wiki_suffix = "&sitefilter=enwiki&format=json"

    wikipedia_url = "https://en.wikipedia.org/wiki/"

    fout = open(args.output_file, 'wb')

    # Create multiple threads for performing the http request and preprocessing
    for i in range(concurrent):
        t = Thread(target = fetch_html_page, args = [fout])
        t.daemon = True
        t.start()
    try:
        extract_urls(args)
        q.join()
    finally:
        fout.close()





