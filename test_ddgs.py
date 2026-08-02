from duckduckgo_search import DDGS

results = DDGS().text("John Maxwell site:vimeo.com", max_results=5)
for r in results:
    print(r['href'], r['title'])

print("---")
results2 = DDGS().videos("Simon Sinek site:facebook.com", max_results=5)
for r in results2:
    print(r.get('content', 'No content'), r.get('title'))
