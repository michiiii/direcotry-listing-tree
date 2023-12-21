# direcotry-listing-tree
Little tool to make a tree out of a page that is vulnerable to directory listing

The script take a directory listing url and outputs a tree of all entries. It goes recursively through the directory listing until it does not find any more directory listings.

```bash
python directory-listing-tree.py --url https://page-with-dirlsting.example
```

