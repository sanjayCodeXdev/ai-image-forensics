"""Quick end-to-end test — POST a synthetic JPEG to /api/analyze."""
import json
import urllib.request
from io import BytesIO

from PIL import Image


def make_jpeg_bytes(w=200, h=200, color=(120, 80, 200)):
    img = Image.new("RGB", (w, h), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def post_multipart(url, field_name, filename, file_bytes, mime="image/jpeg"):
    boundary = "----TestBoundaryXYZ1234"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=30)


def main():
    print("Building test JPEG …")
    img_bytes = make_jpeg_bytes()

    print("POSTing to /api/analyze …")
    try:
        r = post_multipart(
            "http://localhost:8000/api/analyze",
            "file", "test.jpg", img_bytes
        )
        resp = json.loads(r.read().decode())
        print("SUCCESS!")
        print(f"  analysis_id    : {resp.get('analysis_id')}")
        print(f"  final_result   : {resp.get('final_result')}")
        print(f"  confidence_score: {resp.get('confidence_score')}")
        print(f"  ai_probability : {resp.get('ai_probability')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body[:800]}")
    except Exception as ex:
        print(f"Error: {ex}")


if __name__ == "__main__":
    main()
