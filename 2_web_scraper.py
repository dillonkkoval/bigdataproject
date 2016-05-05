'''Thank you to Hitchiker's Guide to python:http://docs.python-guide.org/en/latest/scenarios/scrape/'''
from pyspark import SparkConf, SparkContext
import sys
import re

from lxml import html

import requests
import unicodedata

from variables import MACHINE, VUID, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN

#page = requests.get('http://www.cnn.com/2014/01/18/health/fish-oil-recovery/', stream=True)
#content = page.content
#f = open('workfile', 'r+')
#f.write();
#f.close()

links_file_location = 'hdfs:///user/brewereg/fpout/links_file'
links_and_content = 'hdfs:///user/brewereg/fpout/links_content'

def append_scrapings(spark, links_file):
    links_data = spark.textFile(links_file)
    #links_data = links_data.map(lambda line: eval(line)) \
    #.map(lambda x: (x[0],x[1],x[2],x[4],getPageContent(x[2])))
    links_data = links_data.map(lambda line: eval(line))
    links_data = links_data.map(lambda x: (x[0],x[1],x[2],x[4],getPageContent(x[2])))

    #links_and_content_data = links_data.map(lambda line: eval(line))
   
    #links_data = links_data.map(lambda x: x.append(getPageContent(x[2])))
    links_data.saveAsTextFile(links_and_content)

def getPageContent(url_data):
    rawurl = unicode(url_data)
    asciiurl = ''.join(i for i in rawurl if ord(i)<128)
    index = asciiurl.find("http")
    finalurl = str(asciiurl[index:])
    try:
        r = requests.get(url=finalurl)         
    except requests.exceptions.RequestException as e:
        r = None
    if r is not None:
        return r.content
    else:
        return None
#tree = html.fromstring(page.text)
#f = open('workfile', 'r+')
#f.write(page.content);
#f.close()
#This will create a list of buyers:
#buyers = tree.xpath('//div[@title="buyer-name"]/text()')
#This will create a list of prices
#`prices = tree.xpath('//span[@class="item-price"]/text()')

if __name__ == '__main__':
    conf = SparkConf()
    if sys.argv[1] == 'local':
        conf.setMaster("local[3]")
        print 'Running locally'
    elif sys.argv[1] == 'cluster':
        conf.setMaster("spark://10.0.22.241:7077")
        print 'Running on cluster'
    conf.set("spark.executor.memory","10g")
    conf.set("spark.driver.memory","10g")
    spark = SparkContext(conf = conf)
    append_scrapings(spark, links_file_location)



