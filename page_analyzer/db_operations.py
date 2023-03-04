def get_all_urls(db):
    curr = db.cursor()
    curr.execute("SELECT * FROM urls;")
    urls_ = curr.fetchall()
    last_checks = {}
    last_code = {}
    for url in urls_:
        curr.execute(f"SELECT created_at, status_code, h1,\
                      title, description FROM url_checks"
                     f" WHERE url_id = '{url[0]}' ORDER BY"
                     f" created_at DESC LIMIT 1;")
        actual_info = curr.fetchone()
        last_checks[url[0]] = actual_info[0]
        last_code[url[0]] = actual_info[1]
    curr.close()
    return (urls_, last_checks, last_code)
