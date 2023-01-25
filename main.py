from threading import Thread
import json
import re
from html2text import html2text
import wikitextparser as wtp
import argparse

def format_article(title, content):
    body = title.strip() + '\n'
    for i in range(len(title.strip())):
        body += '='
    body += '\n\n'

    content = re.sub(r'\{\|(.*)\|\}', r'', content, flags=re.S) # remove tables
    content = wtp.parse(content).plain_text()  # wiki to plaintext
    #content = re.sub('\<br\>|\<br/\>|\<br /\>', '\n', content) # well, we ignore newlines...
    content = content.strip()
    content = re.sub(r'\r', r'', content)
    content = re.sub('\n{3,}', '\n', content)  # replace excess whitespace
    content = re.sub(r'&nbsp;', r' ', content)  # remove non-breakable spaces
    content = re.sub(r'\<(.*)\>', r'', content, flags=re.S)  # remove html

    body += content

    return body

def analyze_chunk(text):
    try:
        if '<redirect title="' in text:
            # This is just hyperlink, ignore
            return None
        if '(disambiguation)' in text:
            # This is disambiguation, which is effectively a bunch of hyperlinks, ignore
            return None
        else:
            # We are reading article, continue
            # Obtain title
            title = text.split('<title>')[1].split('</title>')[0]
            title = html2text(title)
            if ':' in title:
                # most articles with : in them are not articles we care about
                return None
        # Obtain ID
        serial = text.split('<id>')[1].split('</id>')[0]

        # Obtain article text
        content = text.split('</text')[0].split('<text')[1].split('>', maxsplit=1)[1]

        body = format_article(title, content)

        return {'title': title.strip(), 'body': body.strip() + '\n', 'id': serial.strip()}
    except Exception as oops:
        print(oops)
        return None


def save_to_disk(article, savedir):
    if savedir[-1] != '/':
        savedir += '/'

    # Convert XML to Text
    doc = analyze_chunk(article)
    if doc:
        print('SAVING:', doc['title'])
        filename = doc['id'] + '.txt'
        # Save to disk
        with open(savedir + filename, 'w', encoding='utf-8') as outfile:
            outfile.write(doc['body'])
            outfile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Wikipedia dump\'s XML to human-readable txt files')
    parser.add_argument('--source', type=str, required=False, default='dataset.xml', help='Source XML')
    parser.add_argument('--output-dir', type=str, required=True, help='Output directory')
    args = parser.parse_args()

    print('Reading from ', args.source, ' and writing to ', args.output_dir)

    article = ''
    with open(args.source, 'r', encoding='utf-8') as infile:
        # Read line by line
        for line in infile:
            # Extract <page> attributes
            if '<page>' in line:
                article = ''
            elif '</page>' in line:
                # We got whole <page> body
                Thread(target=save_to_disk, args=(article, args.output_dir)).start()
            else:
                article += line