import multiprocessing
from multiprocessing import Process, Queue, Value
import time
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

def save_to_disk(article, savedir, dumpedArticles, skippedArticles):
    if savedir[-1] != '/':
        savedir += '/'

    # Convert XML to Text
    doc = analyze_chunk(article)
    if doc:
#        print('SAVING:', doc['title'])
        filename = doc['id'] + '.txt'
        # Save to disk
        with open(savedir + filename, 'w', encoding='utf-8') as outfile:
            outfile.write(doc['body'])
            outfile.close()
        dumpedArticles.value += 1
    else:
        skippedArticles.value += 1

def run_worker_thread(queue, dumpedArticles, skippedArticles):
    while True:
        while not queue.empty():
            object = queue.get()
            save_to_disk(object["article"], object["savedir"], dumpedArticles, skippedArticles)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Wikipedia dump\'s XML to human-readable txt files')
    parser.add_argument('--source', type=str, required=False, default='dataset.xml', help='Source XML')
    parser.add_argument('--output-dir', type=str, required=True, help='Output directory')
    args = parser.parse_args()

    print('Reading from ', args.source, ' and writing to ', args.output_dir)

    # Find number of articles
    start_time = time.time()
    totalArticles = 0
    with open(args.source, 'r', encoding='utf-8') as infile:
        # Read line by line
        for line in infile:
            # Extract <page> attributes
            if '</page>' in line:
                # We got article
                totalArticles += 1
        infile.close()
    end_time = time.time()
    print('Found', totalArticles, 'articles, which took', end_time-start_time, 'seconds')

    # Now analyze the texts
    start_time = time.time()
    last_dump_time = time.time()
    dumpedArticles = Value('i', 0)
    skippedArticles = Value('i', 0)
    processes = []
    queues = []
    print('Spawning', multiprocessing.cpu_count(), 'worker threads')
    for i in range(multiprocessing.cpu_count()):
        queue = Queue()
        queues.append(queue)
        p = Process(target=run_worker_thread, args=(queue, dumpedArticles, skippedArticles))
        p.start()
        processes.append(p)
    article = ''
    queue_n = 0
    with open(args.source, 'r', encoding='utf-8') as infile:
        # Read line by line
        for line in infile:
            # Extract <page> attributes
            if '<page>' in line:
                article = ''
            elif '</page>' in line:
                # We got whole <page> body
                # Put it in queue
                queues[queue_n].put({"article": article, "savedir": args.output_dir})
                queue_n += 1
                if queue_n >= len(queues):
                    queue_n = 0
            else:
                article += line

            # Don't allow queues to grow too much
            for queue in queues:
                if queue.qsize() > 50:
                    while not queue.empty():
                        time.sleep(0.01)

            # Print statistics every 10s
            if time.time() - last_dump_time > 10:
                last_dump_time = time.time()
                print('Processed', dumpedArticles.value, '+', skippedArticles.value, '[dumped/skipped] articles (' + "{:.2f}".format((skippedArticles.value+dumpedArticles.value) / totalArticles * 100) + '%), which took', "{:.1f}".format(time.time() - start_time), 'seconds')

    while dumpedArticles.value + skippedArticles.value != totalArticles and time.time() - last_dump_time > 120:
        print('Waiting for all threads to complete their work...')
        time.sleep(5)

    print('Killing worker threads...')
    for p in processes:
        p.terminate()
        p.join()

    end_time = time.time()
    print('Dumped', dumpedArticles.value, 'articles (' + "{:.2f}".format(dumpedArticles.value/totalArticles*100) + '%), which took', "{:.1f}".format(end_time - start_time), 'seconds')