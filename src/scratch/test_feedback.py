import urllib.request, json, urllib.error

data = {
    "feedback": {
        "type": "Bug",
        "description": "This is a much longer test description that should hopefully bypass the short string check.",
        "version": "1.4.0",
        "os_name": "nt",
        "platform": "win32"
    }
}

req = urllib.request.Request(
    'https://eleviewer.vercel.app/api/feedback', 
    data=json.dumps(data).encode('utf-8'), 
    headers={
        'Content-Type':'application/json'
    }
)

try:
    urllib.request.urlopen(req)
    print("Success")
except urllib.error.HTTPError as e:
    print(e.read().decode())
