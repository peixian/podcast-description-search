#!/usr/bin/env python3
import requests
import pandas as pd
import re
import xml.etree.ElementTree as ET
import argparse


def getRss(itunes_podcast_link: str) -> int:
    # itunes_podcast_link should be https://podcasts.apple.com/us/podcast/the-lebanese-politics-podcast/id1372783898
    m = re.search("(?<=id)[0-9]{8,11}", itunes_podcast_link)
    return int(m.group(0))


def getRssFeed(itunes_id: int) -> str:
    # lookup api from http://jsfiddle.net/onigetoc/2mb5C/
    # and https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/LookupExamples.html#//apple_ref/doc/uid/TP40017632-CH7-SW1

    r = requests.get("https://itunes.apple.com/lookup", params={"id": itunes_id})
    #print(r.json()["results"][0]["feedUrl"])
    return r.json()["results"][0]["feedUrl"]


def getUrlAsDf(rss_feed_url: str) -> pd.DataFrame:
    r = requests.get(rss_feed_url)
    items = []
    # no sanitization happens here! Beware of maliciously constructed urls!
    tree = ET.fromstring(r.text)
    # xml channel
    for e in tree[0]:
        if e.tag == "item":
            element_dict = {}
            for val in e:
                # strip out itunes tags:
                tag = re.sub(r"\{.*?\}", "", val.tag)
                element_dict[tag] = str(val.text).lower()
            items.append(element_dict)
    return pd.DataFrame(items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Takes in an itunes podcast id, searches for a specific string, also dumps all the shows to a csv."
    )
    parser.add_argument("itunes_url", type=str, help="URL from itunes for podcast")
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="Specific string to search for. This is quite dumb so the csv with a more complex engine might be better",
        default="",
    )
    parser.add_argument(
        "-o", "--out", type=str, help="Path to dump the results to a csv", default=""
    )
    args = parser.parse_args()

    rss_id = getRss(args.itunes_url)
    # rss_id = getRss("https://podcasts.apple.com/us/podcast/the-lebanese-politics-podcast/id1372783898")
    feed_url = getRssFeed(rss_id)
    print(f"Feed URL: {feed_url}")
    df = getUrlAsDf(feed_url)
    if args.query != "":
        print(df[df["summary"].str.contains("trash")])
    else:
        print(df.head())
    if args.out != "":
        df.to_csv(args.out)
