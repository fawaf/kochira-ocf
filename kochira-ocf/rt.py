"""
Trrbl rt
"""

from kochira.service import Service
from kochira.service import background
import re
import time
import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error

service = Service(__name__, __doc__)

RT_ENDPOINT = "https://rt.ocf.berkeley.edu"
MAX_RESULTS = 10
MIN_NOTIFY = 3

def read(uri):
  access_user = 'ircbot'
  access_password = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
       
  # trying login on rt server
  cj = http.cookiejar.LWPCookieJar()
  opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
  urllib.request.install_opener(opener)
  data = {'user': access_user, 'pass': access_password}
  ldata = urllib.parse.urlencode(data)
  binary_data = ldata.encode('ASCII')
  login = urllib.request.Request(uri, binary_data)
  try:
    response = urllib.request.urlopen(login).read()
    return response
  except urllib.error.URLError:
    return ""

def get(num):
  try:
    num = int(num)
  except ValueError:
    return "That's not numeric."

  uri = "{endpoint}/REST/1.0/ticket/{num}/show".format(endpoint = RT_ENDPOINT, num = num)

  response = str(read(uri), encoding='utf8')
  if response == "":
    return "Communication error"
  if "does not exist" in response:
    return "Ticket {num}: No such ticket".format(num = num)
  m = re.findall("((?:Queue|Owner|Creator|Subject|Status):.*)", response)
  fields = [_.split(": ", 1)[1] for _ in m]
  return "Ticket {num}: {status} {url}".format(num = num, status = "/".join(fields), url = "{endpoint}/t/{num}".format(endpoint = RT_ENDPOINT, num = num))

def last(how_many):
  try:
    how_many = int(how_many)
  except ValueError:
    return "That's not numeric."

  weeks_ago = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 14 * 60 * 60 * 24))
  query = "raw id != 0 and LastUpdated > '{t}' and (Status = 'new' or Status = 'open' or Status = 'stalled')".format(t = weeks_ago)
  results = search_full(query)
  return results[1:min(len(results), how_many + 1)]

def search_full(what):
  statusen = ["new", "open", "stalled"]
  if what is not None and len(what.split(" ")) > 1 and what.split(" ")[0] == "all":
    statusen.append("resolved")

  status_query = " OR ".join(["Status = '" + _ + "'" for _ in statusen])
  uri = "{endpoint}/REST/1.0/search/ticket?".format(endpoint = RT_ENDPOINT)  + urllib.parse.urlencode({"query": "Content = '{what}' and ({status_query})".format(what = what, status_query = status_query), "orderby": "-Created"})

  if what is not None and len(what.split(" ")) > 1 and what.split(" ")[0] == "raw":
    uri = "{endpoint}/REST/1.0/search/ticket?".format(endpoint = RT_ENDPOINT) + urllib.parse.urlencode({"query": " ".join(what.split(" ")[1:]), "orderby": "-Created"})

  response = str(read(uri), encoding='utf8')
  if response == "":
    return ["Communication error"]

  if "No matching results" in response:
    return ["Search '{what}': No search results".format(what = what)]

  m = re.findall("((?:\d+):.*)", response)
  results = [_.split(": ")[0] for _ in m]

  if len(results) > MAX_RESULTS:
    out = ["Only showing {max} of {total} results".format(max = MAX_RESULTS, total = len(results))]
  else:
    out = []

  for ticket in results[:min(len(results), MAX_RESULTS)]:
    out.append(get(ticket))

  if len(results) > MIN_NOTIFY:
    out.append("End of results")

  return out

@service.command(r"!rt (?P<command>t(?:icket)?|s(?:earch)?|last10|last|help)(?: (?P<args>.*))?")
def rt_command(ctx, command, args):
    """
    RT
    """
    if command in ["t", "ticket"]:
        out = get(args)
        ctx.message(out)

    elif command in ["s", "search"]:
        out = search_full(args)
        for l in out:
            ctx.message(l)

    elif command == "last10":
        out = last(10)
        for l in out:
            ctx.message(l)

    elif command == "last":
        out = last(args)
        for l in out:
            ctx.message(l)

    elif command == "help":
        msg = ["!rt (t|ticket) <num>: Look up ticket details",
            "!rt (s|search) (all) <string>: Search fulltext (search all for resolved tickets too)",
            "!rt last10: Show last 10 created tickets",
            "!rt last <num>: Show last <num> created tickets",
            "List format: queue/owner/requestor/subject/status url"]
        for l in msg:
            ctx.message(l)

@service.hook("channel_message", priority=2000)
def rt(ctx, target, origin, message):
    INLINE_MENTION_EXPR = re.compile("(?:RT|rt)\s?#(\d+)")
    inline_match = INLINE_MENTION_EXPR.findall(message)

    if inline_match is not []:
        for num in inline_match:
            out = get(num)
            ctx.message(out)
