import chardet # Let's see if we can just open with utf-16 or utf-8

def check_file(path):
    print(f"=== {path} ===")
    with open(path, "rb") as f:
        raw = f.read(200)
        print("Raw bytes:", raw[:20])
    
    # Try different decodings
    for enc in ["utf-16", "utf-16-le", "utf-16-be", "utf-8", "cp1251"]:
        try:
            with open(path, "r", encoding=enc) as f:
                content = f.read(200)
                print(f"  {enc}: SUCCESS (first 50 chars): {repr(content[:50])}")
        except Exception as e:
            print(f"  {enc}: FAILED - {e}")

check_file("index.html")
check_file("index_ghpages.html")
