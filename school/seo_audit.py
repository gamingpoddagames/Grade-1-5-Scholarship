#!/usr/bin/env python3
"""Offline SEO guardrails for the public Sinhala school site.

Checks only actual build files; never claims Google has crawled or indexed them.
"""
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlparse

BASE = "https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"

class HtmlAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta={}
        self.links=[]
        self.ids=set()
        self.ld_json=[]
        self._script_json=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get("id"): self.ids.add(d["id"])
        if tag=="meta":
            self.meta[d.get("name") or d.get("property")]=d.get("content","")
        if tag=="link": self.links.append(d)
        if tag=="a" and d.get("href"): self.links.append(d)
        if tag=="script" and d.get("type")=="application/ld+json": self._script_json=True
    def handle_data(self,data):
        if self._script_json:self.ld_json.append(data)
    def handle_endtag(self,tag):
        if tag=="script":self._script_json=False

def audit(root):
    page=(root/"index.html").read_text(encoding="utf-8")
    parsed=HtmlAudit()
    parsed.feed(page)
    assert '<html lang="si">' in page, "Sinhala language must be declared"
    assert len(parsed.meta.get("description",""))>=70, "Meaningful description missing"
    assert parsed.meta.get("robots")=="index,follow", "Homepage must not be noindex"
    assert any(x.get("rel")=="canonical" and x.get("href")==BASE for x in parsed.links), "Incorrect canonical"
    scripts=[json.loads(x) for x in parsed.ld_json if x.strip()]
    assert any(x.get("@type")=="WebSite" and x.get("url")==BASE for x in scripts), "Website schema missing"
    anchors=[x for x in parsed.links if x.get("href","").startswith("#")]
    missing=[x["href"] for x in anchors if x["href"][1:] not in parsed.ids]
    assert not missing, "Broken homepage anchors: "+str(missing[:8])
    expected={"papers","past-papers","exam-results","story-books","quiz","videos","blog"}
    assert expected.issubset(parsed.ids), "Missing learning sections: "+str(expected-parsed.ids)
    assert any(x.get("href","").startswith("https://punchinanamaga.blogspot.com/") for x in parsed.links), "Missing Blogger internal ecosystem link"
    sitemap=root/"sitemap.xml"
    if sitemap.exists():
        tree=ET.parse(sitemap)
        ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls=[n.text for n in tree.findall(".//s:loc",ns)]
        assert len(urls)>=25, "Sitemap unexpectedly small"
        assert len(urls)==len(set(urls)), "Duplicate URLs in sitemap"
        assert all(urlparse(u).netloc=="gamingpoddagames.github.io" for u in urls), "Unrelated sitemap host"
        assert BASE in urls, "Homepage missing in sitemap"
    print(f"SEO AUDIT PASSED: lang=si, description, canonical, schema, {len(anchors)} anchor links, Blogger links, sitemap.")
if __name__=="__main__":
    audit(pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path("."))
