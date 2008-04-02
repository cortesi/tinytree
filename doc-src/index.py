import countershape.widgets
import countershape.layout
import countershape.grok
from countershape.doc import *

ns.docTitle = "Tinytree Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "aldo@nullcube.com"
ns.foot = "Copyright Nullcube 2008"
ns.head = readFrom("_header.html")
ns.sidebar = countershape.widgets.SiblingPageIndex('/index.html', exclude=['countershape'])
this.layout = countershape.layout.TwoPane("yui-t2", "doc3")
this.titlePrefix = "TinyTree Manual - "

ns.ctgrok = countershape.grok.grok("../tinytree.py")
ns.example = readFrom("_example.py")

pages = [
    Page("index.html", "Introduction"),
    Page("api.html", "API"),
    Page("admin.html", "Administrivia")
]
