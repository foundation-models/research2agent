#!/usr/bin/env python3
"""
share2containers.py
-------------------
Fetch a public ChatGPT *Share* link, keep only the assistant messages,
convert them to Markdown (links preserved), slice into ~350-token chunks
with 50-token overlap, and pack the chunks into ≤20 container files
ready for Custom GPT upload.

Usage
-----
python share2containers.py \
       --url  https://chat.openai.com/share/abc123 \
       --slug humana_dental \
       --out  ./containers

Requires: requests, beautifulsoup4, html2text, tiktoken  (pip install …)
"""
import argparse, re, requests, textwrap, tiktoken
from pathlib import Path
from bs4 import BeautifulSoup
import html2text, itertools, math, uuid, os

# ---------- config ----------
MAX_CHUNK_TOKENS = 350
OVERLAP_TOKENS   = 50
PACK_TOK_LIMIT   = 95_000        # stay well under internal 2 M limit
PACK_BYTE_LIMIT  = 18_000_000    # ≈18 MB per file
enc = tiktoken.get_encoding("cl100k_base")
# -----------------------------

def toklen(txt:str)->int: return len(enc.encode(txt))

def fetch_html(url:str)->str:
    r = requests.get(url, timeout=30,
                     headers={"User-Agent":"Mozilla/5.0 (share2containers)"})
    r.raise_for_status()
    return r.text

def assistant_html_to_md(html:str)->str:
    soup = BeautifulSoup(html, "html.parser")
    md_blocks=[]
    for art in soup.find_all("article"):
        if art.get("data-message-author-role")=="assistant":
            md_blocks.append(html2text.html2text(str(art)))
    return "\n\n".join(md_blocks)

def chunk_text(md:str,max_toks:int=350,overlap:int=50):
    tokens = enc.encode(md)
    i=0
    while i < len(tokens):
        j=min(i+max_toks,len(tokens))
        yield enc.decode(tokens[i:j])
        i = j-overlap

def pack_chunks(chunks, slug, out_dir:Path):
    file_idx=1; buf=[]; buf_tok=0; buf_bytes=0
    for n,chunk in enumerate(chunks,1):
        hdr=f"### [{slug}] – part {n}\n\n"
        chunk_blob = hdr+chunk.strip()+"\n"
        t=toklen(chunk_blob); b=len(chunk_blob.encode())
        if (buf_tok+t>PACK_TOK_LIMIT) or (buf_bytes+b>PACK_BYTE_LIMIT):
            _write(buf, slug, file_idx, out_dir); file_idx+=1; buf=[]; buf_tok=0; buf_bytes=0
        buf.append(chunk_blob); buf_tok+=t; buf_bytes+=b
    if buf: _write(buf, slug, file_idx, out_dir)

def _write(lines, slug, idx, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}_container_{idx:02}.md"
    path.write_text("".join(lines), encoding="utf-8")
    print(f"✓ wrote {path}  ({toklen(''.join(lines))} tokens)")

def main(url:str, slug:str, out_dir:Path):
    print("Fetching share page …")
    html = fetch_html(url)
    print("Converting assistant messages → Markdown …")
    md   = assistant_html_to_md(html)
    print("Chunking and packing …")
    chunks = list(chunk_text(md, MAX_CHUNK_TOKENS, OVERLAP_TOKENS))
    pack_chunks(chunks, slug, out_dir)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="public Share URL")
    p.add_argument("--slug", required=True, help="short id used in headers & filenames")
    p.add_argument("--out",  required=True, type=Path, help="output directory")
    args=p.parse_args()
    main(args.url, args.slug, args.out)
