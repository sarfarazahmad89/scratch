### All my random python scribbles lie here ###
Scripts are usually available as an entrypoint.
#### pydownloader ####
- Using httpx, asyncio and multiple tcp connections to download a file, fast!
- Example 
```
(venv) [ahmad@mymachine scratch]$ pydownloader --help

 Usage: pydownloader [OPTIONS] URL

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    url      TEXT  [default: None] [required]                                                                                                                                                                    │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│         -o      TEXT     short or full path to the target file                                                                                                                                                    │
│         -n      INTEGER  number of parallel connections to use for the download [default: 8]                                                                                                                      │
│         -t      FLOAT    timeout seconds for network inactivity [default: 15]                                                                                                                                     │
│ --help                   Show this message and exit.                                                                                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```




