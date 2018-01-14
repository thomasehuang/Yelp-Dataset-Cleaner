#!/usr/bin/python3

import sys
import json
import csv
import argparse
from langdetect import detect

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, help='Input data file. Must be in JSON.',
                    default='review1.json')
parser.add_argument('-o', '--out', type=str, help='Output data file. Will be in csv.',
                    default='dataset.csv')
parser.add_argument('-np', '--num-positive', type=str, help='Number of positive data points.',
                    default=int(1e3))
parser.add_argument('-nn', '--num-negative', type=str, help='Number of negative data points.',
                    default=int(1e3))

def main():
    args = parser.parse_args()

    input_file = args.input
    output_file = args.out
    num_data1 = int(args.num_positive)
    num_data2 = int(args.num_negative)

    json_lines = [json.loads(l.strip()) for l in open(input_file).readlines()]

    OUT_FILE = open(output_file, "w")
    root = csv.writer(OUT_FILE)
    root.writerow(['content','label','rating'])

    bad_words1 = [l.replace('\n','').strip() for l in open('bad_words.txt').readlines()]
    bad_words2 = [l.replace('\n','').strip() for l in open('bad_words2.txt').readlines()]

    positive = []
    negative = []
    neutral = []

    num_filtered = 0

    for line in json_lines:
        # checks to prevent extra work
        if len(positive) == num_data1 and len(negative) == num_data2 and len(neutral) == num_data2:
            break
        if len(positive) == num_data1 and line['stars'] > 3:
            continue
        elif len(negative) == num_data2 and line['stars'] < 3:
            continue
        elif len(neutral) == num_data2 and line['stars'] == 3:
            continue

        text = line['text'].replace('\n',' ')

        # FILTERS FOR TEXT
        # language
        if detect(text) != 'en':
            num_filtered += 1
            continue
        # links
        if 'http://' in text.lower() or 'https://' in text.lower():
            num_filtered += 1
            continue
        # bad words
        bad = False
        for bad_word in bad_words1:
            if bad_word in text.lower().split():
                bad = True
                # print(bad_word)
                # print(text)
                # input('enter to continue')
                break
        if not bad:
            for bad_word in bad_words2:
                if bad_word in text.lower():
                    bad = True
                    # print(bad_word)
                    # print(text)
                    # input('enter to continue')
                    break
        if bad:
            num_filtered += 1
            continue

        if line['stars'] > 3:
            positive.append([text,1,1])
        elif line['stars'] == 3:
            rating = 0
            label = -1
            neutral.append([text,-1,0])
        else:
            rating = -1
            label = -1
            negative.append([text,-1,-1])

    for l in positive:
        root.writerow(l)
    for l in negative:
        root.writerow(l)
    for l in neutral:
        root.writerow(l)

    OUT_FILE.close()

    print('%i data points filtered out' % (num_filtered,))


if __name__ == '__main__':
    main()