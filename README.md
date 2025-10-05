# Git: common_crawl
Study the common-crawl dataset
 - [Common Crawl](https://commoncrawl.org/)
 - open corpus since 2007
 - by 2025/10, there are 300B pages
 - 3–5 billion new pages added each month
 - index: https://index.commoncrawl.org/collinfo.json


# Download Common Crawl datasets
- AWS
  - bucket s3://commoncrawl/, 
  - located in the US-East-1 (Northern Virginia) AWS Region.
- Https: Example CC-MAIN-20130516092621-00000-ip-10-60-113-184.ec2.internal.warc.gz(https://data.commoncrawl.org/commoncrawl/crawl-data/CC-MAIN-2013-20/segments/1368696381249/warc/CC-MAIN-20130516092621-00000-ip-10-60-113-184.ec2.internal.warc.gz) 

# WET vs WAT vs WARC
---
## WET File
WET files contain extracted plain text.

Much smaller and easier to process than full WARC archives.
### Extract the WET file
```
python common_crawl_wet_wat.py --wet
```

## WAT File
WAT files have metadata.

Much smaller and easier to process than full WARC archives.
### Extract the WAT file
```
python common_crawl_wet_wat.py --wat
```


## WARC (Web ARChive) format 
### What's in a WARC Record?
- Content: The raw HTML of the web page itself. 
- Request Headers: Details of the HTTP request made to fetch the page. 
- Response Headers: Information about the response from the web server, such as  content type and encoding. 
- Metadata: Information about the crawl, including the URL, fetch time, content digest, and MIME type. 
- New Record Types: WARC can also store other related resources, such as request/response records and metadata. 

### Extract the Warc file
```
python common_crawl.py
```


# Example Common-crawl Data
- common_crawl_example1.html: example html content 
- common_crawl_exmaple1_beautifulsope_lxml.html: above example1 cleaned via BeatifulSoup lxml parser. 


# Common LLM dataset from CommonCrawl
---
## FineWeb-Edu 
- [HuggingFaceFW](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/viewer/default/train)
- [The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale](https://arxiv.org/pdf/2406.17557)

## DCLM 