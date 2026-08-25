"""Follow an OSF node to whatever actually holds its files, and say what is there.

WHY THIS EXISTS. The paper this sits beside establishes that sharing analysis
code raises the probability of reproducing a paper by ~38 percentage points. Its
own Data Availability statement names two OSF nodes. One of them holds nothing,
and finding that out takes six API calls that nobody makes, because the node's
web page returns 200 and looks perfectly alive.

An OSF node can hold files in several ways and a check that looks at only the
default one is worse than no check:

  osfstorage         files deposited in OSF itself. Persistent.
  a provider add-on  github / dropbox / s3 / figshare. **A POINTER.** It inherits
                     the lifetime of whatever it points at, and OSF will keep
                     serving the node long after the target is gone.
  child components   sub-nodes, each with its own storage. A parent can look
                     nearly empty while the material sits one level down --
                     which is the case for the OTHER node of this same paper.

So the audit is: metadata, every provider, file counts per provider, children,
the wiki (which often names locations the statement does not), the add-on's
configured target, and then that target's own liveness at its own API.

This is the check `kb.py links` cannot currently do. That command asks whether a
URL answers; here the URL answers and the artifact is gone.

Usage:  python audit_osf_artifacts.py [node_id ...]      default: the two in the paper
"""
import json
import sys
import urllib.request

OSF = "https://api.osf.io/v2"
UA = {"User-Agent": "zoo-kb-artifact-audit/1.0", "Accept": "application/vnd.api+json"}


def get(url, headers=UA):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return getattr(e, "code", None), {"_error": type(e).__name__ + ": " + str(e)[:120]}


def gh(path):
    code, body = get("https://api.github.com/" + path,
                     {"User-Agent": UA["User-Agent"], "Accept": "application/vnd.github+json"})
    return code, body


def audit(node):
    print("=" * 74)
    print("OSF node %s   https://osf.io/%s/" % (node, node))
    print("=" * 74)
    code, d = get("%s/nodes/%s/" % (OSF, node))
    if "_error" in d or "data" not in d:
        print("  node metadata unavailable: %s" % d.get("_error", code))
        return
    a = d["data"]["attributes"]
    print("  title    : %s" % (a.get("title") or "")[:96])
    print("  public   : %s   modified: %s" % (a.get("public"), a.get("date_modified")))

    code, d = get("%s/nodes/%s/files/" % (OSF, node))
    providers = [i["attributes"].get("provider") for i in d.get("data", [])]
    print("  providers: %s" % (", ".join(providers) or "(none)"))

    for p in providers:
        code, d = get("%s/nodes/%s/files/%s/" % (OSF, node, p))
        items = d.get("data", [])
        print("  %-12s %d item(s)" % (p + ":", len(items)))
        for i in items[:8]:
            at = i["attributes"]
            print("      %-6s %-40s %s" % (at.get("kind"), (at.get("name") or "")[:40],
                                           at.get("size")))
        if p == "github":
            code, d = get("%s/nodes/%s/addons/github/" % (OSF, node))
            tgt = ((d.get("data") or {}).get("attributes") or {}).get("folder_id")
            print("      add-on target: %r" % tgt)
            if tgt:
                repo = str(tgt).rstrip(":").split(":")[0]
                c, body = gh("repos/" + repo)
                print("      github.com/%s -> HTTP %s   %s"
                      % (repo, c, "" if c == 200 else body.get("message", "")))
                if c != 200:
                    owner = repo.split("/")[0]
                    c2, lst = gh("users/%s/repos?per_page=100" % owner)
                    if isinstance(lst, list):
                        print("      account %s is %s with %d public repo(s): %s"
                              % (owner, "LIVE" if c2 == 200 else "?", len(lst),
                                 ", ".join(r["name"] for r in lst[:8])))
                        print("      -> the target is not merely renamed within this account")

    code, d = get("%s/nodes/%s/children/?page[size]=100" % (OSF, node))
    kids = d.get("data", [])
    print("  children : %d" % len(kids))
    for k in kids[:6]:
        print("      %s  %s" % (k["id"], (k["attributes"].get("title") or "")[:56]))
    if len(kids) > 6:
        print("      ... and %d more" % (len(kids) - 6))

    code, d = get("%s/nodes/%s/wikis/" % (OSF, node))
    for w in d.get("data", []):
        link = w["links"].get("download")
        if not link:
            continue
        # The wiki content endpoint returns PLAIN TEXT, not JSON. The first
        # version ran it through the JSON getter and printed a decode error
        # where the wiki text should be -- which, in a script whose subject is
        # "the fetch answered and the content is not what you assumed", was too
        # apt to leave standing.
        try:
            req = urllib.request.Request(link, headers={"User-Agent": UA["User-Agent"]})
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = r.read().decode("utf-8", "replace")
        except Exception as e:
            txt = "<unfetchable: %s>" % type(e).__name__
        print("  wiki %-8s %s" % (w["attributes"].get("name"),
                                  " ".join(txt.split())[:220]))
    print()


if __name__ == "__main__":
    nodes = sys.argv[1:] or ["3bzu8", "3x2y6"]
    for n in nodes:
        audit(n)
    print("READ THE PROVIDER LINE. A node whose only provider is a pointer holds")
    print("nothing of its own, and its web page will answer 200 for as long as OSF")
    print("exists. Sharing is not depositing.")
