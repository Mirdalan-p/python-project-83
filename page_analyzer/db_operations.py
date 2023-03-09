

def get_all_urls(db):
    curr = db.cursor()
    curr.execute("SELECT * FROM urls;")
    urls = curr.fetchall()
    checks = {}
    status_codes = {}
    for url in urls:
        curr.execute(f"SELECT created_at, status_code, h1,\
                      title, description FROM url_checks"
                     f" WHERE url_id = '{url[0]}' ORDER BY"
                     f" created_at DESC LIMIT 1;")
        actual_info = curr.fetchone()
        if actual_info:
            checks[url[0]] = actual_info[0]
            status_codes[url[0]] = actual_info[1]
        else:
            checks[url[0]] = ''
            status_codes[url[0]] = ''
    curr.close()
    return {'urls': urls, 'checks': checks, 'status_codes': status_codes}
