import json
import os

from bs4 import BeautifulSoup

from paths import DATA_DIR


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    soup = soup.find("div", class_="the-document-body ndthaydoi noidungtracuu")
    if not soup:
        return ""
    return soup.get_text(strip=True, separator="\n")


if __name__ == "__main__":
    os.makedirs(DATA_DIR / "processed/text", exist_ok=True)
    os.makedirs(DATA_DIR / "unstructured", exist_ok=True)

    html_dir = DATA_DIR / "raw/html"
    file_need_debug = []
    for file in os.listdir(html_dir):
        if file.endswith(".html"):
            with open(os.path.join(html_dir, file), "r", encoding="utf-8") as f:
                html_content = f.read()
                extracted = extract_text(html_content)
                if not extracted:
                    file_need_debug.append(file)
                    continue
                base_name = os.path.splitext(file)[0]
                out_path = os.path.join(
                    DATA_DIR / "processed/text", f"{base_name}.txt"
                )
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(extracted)

    if file_need_debug:
        with open(
            DATA_DIR / "unstructured/file_need_debug.json", "w", encoding="utf-8"
        ) as f:
            json.dump(file_need_debug, f, ensure_ascii=False, indent=2)
