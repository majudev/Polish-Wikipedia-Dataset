import os

folder = "output"
output_file = "fullwiki.txt"

with open(output_file, 'w') as outfile:
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename)) as infile:
            outfile.write(infile.read())
