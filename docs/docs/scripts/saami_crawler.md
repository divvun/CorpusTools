# saami_crawler

Add files to freecorpus from a given site.

Only able to crawl samediggi.no or www.samediggi.fi, will collect html files only for now.

Run it like this:

```sh
saami_crawler samediggi.no
```

The complete help text from the program is as follows:

```sh
usage: saami_crawler [-h] [-v] sites [sites ...]

Crawl saami sites (for now, only samediggi.no and www.samediggi.fi).

positional arguments:
  sites          The sites to crawl

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```
