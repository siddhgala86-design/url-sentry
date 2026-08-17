"""
URL Sentry — Phishing URL Detector (Decision Support App)
SYBSCIT (NEP) — Python Programming, Units I-IV

Every URL is passed through 5 checks. Each failed check adds points to a
risk score, and the score becomes a plain-language recommendation. That
reasoning is what makes this "decision support" and not just a checker.
"""

import re
import json
import os
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "scan_history.txt")

# Unit II: list, tuple, set — three collection types, each picked for a reason.
BAIT_WORDS = ["login", "verify", "update", "secure", "account", "confirm",
              "banking", "password", "urgent", "unlock", "free", "bonus"]

RISKY_TLDS = {"zip", "xyz", "top", "gq", "tk", "ml", "cf", "click", "loan"}

TRUSTED_BRANDS = ("google", "facebook", "paypal", "amazon", "microsoft",
                   "apple", "netflix", "icicibank", "hdfcbank", "sbi")


class URLAnalyzer:
    """Unit IV: class + object. One object = one URL scan."""

    def __init__(self, raw_url):
        self.raw_url = raw_url.strip()
        self.domain = ""
        self.report = {
            "url": self.raw_url,
            "checks": [],
            "risk_score": 0,
            "verdict": None,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _flag(self, name, ok, points, message):
        """Unit II: function with parameters. Adds one check result."""
        self.report["checks"].append({
            "name": name, "status": "pass" if ok else "flag", "message": message
        })
        if not ok:
            self.report["risk_score"] += points

    # ---- Check 1: Structure validation ---------------------------------
    def check_structure(self):
        pattern = r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:\d+)?(/.*)?$"
        try:
            url = self.raw_url if self.raw_url.startswith(("http://", "https://")) \
                else "http://" + self.raw_url
            parsed = urlparse(url)
            self.domain = parsed.netloc.lower().split("@")[-1].split(":")[0]

            ok = bool(re.match(pattern, self.raw_url)) and "." in self.domain
            self._flag("Structure Validation", ok, 40,
                        "Looks like a valid web address." if ok else
                        "Not a valid URL structure (missing/malformed domain).")
        except Exception as err:                       # Unit III: exception handling
            self._flag("Structure Validation", False, 40, f"Could not parse URL ({err}).")

    # ---- Check 2: Suspicious domain rule --------------------------------
    def check_domain(self):
        issues = []
        tld = self.domain.split(".")[-1] if "." in self.domain else ""

        if tld in RISKY_TLDS:
            issues.append(f"high-risk domain extension '.{tld}'")
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", self.domain):
            issues.append("raw IP address instead of a domain name")

        # Unit II: list comprehension over a tuple
        fake_brands = [b for b in TRUSTED_BRANDS
                        if b in self.domain and not self.domain.endswith(b + ".com")]
        if fake_brands:
            issues.append(f"mimics brand name(s): {', '.join(fake_brands)}")

        ok = not issues
        self._flag("Suspicious Domain Rule", ok, 25,
                    "Domain looks normal." if ok else "; ".join(issues))

    # ---- Check 3: Character anomaly detection ---------------------------
    def check_characters(self):
        url = self.raw_url
        issues = []

        if len(url) > 75:
            issues.append("unusually long URL")
        if url.count("-") >= 4:
            issues.append("too many hyphens")
        if "@" in url:
            issues.append("'@' symbol hides the real destination")
        if re.search(r"\d{5,}", url):
            issues.append("long digit sequence")

        hits = [w for w in BAIT_WORDS if w in url.lower()]
        if hits:
            issues.append(f"bait word(s): {', '.join(hits[:3])}")

        ok = not issues
        self._flag("Character Anomaly Detection", ok, 20,
                    "No suspicious characters found." if ok else "; ".join(issues))

    # ---- Check 4 & 5: Risk score -> verdict -> recommendation -----------
    def finalize(self):
        score = self.report["risk_score"]
        if score == 0:
            verdict = "SAFE"
        elif score <= 30:
            verdict = "SUSPICIOUS"
        else:
            verdict = "DANGEROUS"

        messages = {
            "SAFE": "No red flags found. Looks safe to open.",
            "SUSPICIOUS": "Some warning signs found — avoid entering personal info.",
            "DANGEROUS": "Multiple phishing indicators found. Do not open this link.",
        }
        self.report["verdict"] = verdict
        self.report["recommendation"] = messages[verdict]

    def run(self):
        self.check_structure()
        self.check_domain()
        self.check_characters()
        self.finalize()
        save_scan(self.report)          # Unit IV: file handling
        return self.report


# --- File handling: write + read the scan log --------------------------
def save_scan(report):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(report) + "\n")
    except OSError as err:
        print(f"Could not write log: {err}")


def load_history(limit=8):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    lines.reverse()
    return [json.loads(line) for line in lines if line.strip()]


# --- Routes --------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html", history=load_history())


@app.route("/analyze", methods=["POST"])
def analyze():
    url = (request.get_json(silent=True) or {}).get("url", "")
    if not url:
        return jsonify({"error": "Please enter a URL."}), 400
    return jsonify(URLAnalyzer(url).run())


if __name__ == "__main__":
    app.run(debug=True)
