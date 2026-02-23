# streamlit_app.py
import os
import re
import base64
from datetime import date, datetime
from typing import Optional, Dict, Any

import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Brand assets / helpers
# ──────────────────────────────────────────────────────────────────────────────
def _load_logo_assets():
    candidates = [
        os.getenv("ASB_LOGO_PATH"),
        "/var/www/asb-main/assets/asb.logo.jpg",
        "/var/www/asb-main/assets/asb_logo.jpg",
        "/mnt/data/ASB Logo.jpg",
        "ASB Logo.jpg",
        "./assets/asb.logo.jpg",
        "./assets/asb_logo.jpg",
        "./assets/asb_logo.png",
    ]
    for p in candidates:
        if not p:
            continue
        try:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    return f.read(), p
        except Exception:
            continue
    return None, None


def _inject_brand_css():
    magenta = "#ff4bd8"
    violet = "#6a5cff"
    gold = "#f5b400"
    text = "#1b1e28"
    bg = "#ffffff"

    st.markdown(
        f"""
<style>
:root {{
  --asb-magenta: {magenta};
  --asb-violet:  {violet};
  --asb-gold:    {gold};
  --asb-text:    {text};
  --asb-bg:      {bg};
}}
html, body, .stApp {{
  color: var(--asb-text);
  background: var(--asb-bg);
  font-size: 17px;
  line-height: 1.35;
}}
[data-testid="stHeader"] {{
  background: linear-gradient(90deg, var(--asb-magenta), var(--asb-violet));
  border-bottom: 2px solid var(--asb-gold);
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
}}
.block-container {{
  padding-top: 2.0rem !important;
  max-width: 1200px;
}}
section[data-testid="stSidebar"] > div:first-child {{
  background: linear-gradient(135deg,
              rgba(255,75,216,.05),
              rgba(106,92,255,.05));
}}
section[data-testid="stSidebar"] .block-container {{
  padding-top: .6rem !important;
}}
section[data-testid="stSidebar"] hr {{
  margin: 1.0rem 0 .6rem 0 !important;
  opacity: .6;
}}
section[data-testid="stSidebar"] {{
  font-size: 18px;
}}
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {{
  font-size: 1.05em;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(90deg, var(--asb-magenta), var(--asb-violet)) !important;
  border: 0 !important;
  color: #fff !important;
  box-shadow: 0 2px 10px rgba(106,92,255,.22);
  border-radius: 10px;
  padding: .55rem 1.05rem;
  font-size: 0.95em;
}}
.stButton > button[kind="primary"]:hover {{
  filter: brightness(1.02);
}}
.stDownloadButton > button {{
  border-color: var(--asb-gold) !important;
  color: var(--asb-text) !important;
  border-radius: 10px;
}}
h1, .stMarkdown h1 {{
  letter-spacing: .2px;
  margin-top: .4rem;
  font-size: 2.1rem;
}}
h2, .stMarkdown h2 {{
  letter-spacing: .15px;
  font-size: 1.45rem;
}}
h3, .stMarkdown h3 {{
  font-size: 1.15rem;
}}
div[data-baseweb="input"] > div {{
  border-radius: 10px;
}}
.asb-sidebar-logo {{
  display:grid;
  place-items:center;
  padding: .6rem 0 1rem 0;
}}
.asb-sidebar-logo img {{
  width: 140px;
  height: auto;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(106,92,255,.12);
}}
.asb-cards {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: .4rem;
}}
.asb-card {{
  border: 1px solid rgba(106,92,255,.18);
  border-left: 4px solid var(--asb-gold);
  border-radius: 14px;
  padding: 12px 12px 10px 12px;
  background: linear-gradient(135deg, rgba(255,75,216,.04), rgba(106,92,255,.04));
  box-shadow: 0 2px 12px rgba(0,0,0,.04);
}}
.asb-card h4 {{
  margin: 0 0 6px 0;
  font-size: 1.02rem;
}}
.asb-kv {{
  display:flex;
  justify-content:space-between;
  gap: 10px;
  margin: 4px 0;
}}
.asb-kv b {{
  font-size: 1.1rem;
}}
.asb-pillrow {{
  margin-top: 8px;
  display:flex;
  flex-wrap:wrap;
  gap:6px;
}}
.asb-pill {{
  display:inline-block;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(106,92,255,.12);
  border: 1px solid rgba(106,92,255,.18);
  font-size: .83rem;
}}
.asb-muted {{
  opacity: .8;
  font-size: .92rem;
}}
@media (max-width: 1100px) {{
  .asb-cards {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
@media (max-width: 600px) {{
  .asb-cards {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }}
}}
@media (max-width: 900px) {{
  .block-container {{
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-top: 1.4rem !important;
  }}
  html, body, .stApp {{ font-size: 16px; }}
  h1, .stMarkdown h1 {{ font-size: 1.7rem; }}
  h2, .stMarkdown h2 {{ font-size: 1.3rem; }}
  .asb-sidebar-logo img {{ width: 110px; }}
}}
</style>
        """,
        unsafe_allow_html=True,
    )


# ✅ MUST be first Streamlit call
_logo_bytes, _logo_path = _load_logo_assets()
st.set_page_config(
    page_title="ASB Numerology",
    layout="wide",
    page_icon=_logo_path if _logo_path else _logo_bytes
)

if _logo_bytes:
    try:
        st.logo(_logo_bytes, icon_image=_logo_bytes)
    except Exception:
        pass
    _b64 = base64.b64encode(_logo_bytes).decode("utf-8")
    with st.sidebar:
        st.markdown(
            f'<div class="asb-sidebar-logo"><img src="data:image/png;base64,{_b64}" alt="ASB"/></div>',
            unsafe_allow_html=True,
        )

_inject_brand_css()


# ──────────────────────────────────────────────────────────────────────────────
# Safe secrets accessor
# ──────────────────────────────────────────────────────────────────────────────
def _get_secret(name: str, default: str | None = None) -> str | None:
    try:
        has_local_secrets = (
            os.path.exists(os.path.join(os.getcwd(), ".streamlit", "secrets.toml"))
            or os.path.exists(os.path.expanduser("~/.streamlit/secrets.toml"))
        )
        on_cloud = bool(os.getenv("STREAMLIT_RUNTIME"))

        if on_cloud or has_local_secrets:
            return st.secrets.get(name, default)  # type: ignore[attr-defined]
    except Exception:
        pass
    return os.getenv(name, default)


# ──────────────────────────────────────────────────────────────────────────────
# Config
# Streamlit talks ONLY to FastAPI (8000). FastAPI proxies auth to MERN.
# ──────────────────────────────────────────────────────────────────────────────
API_BASE = (_get_secret("ASB_API_BASE", "https://api.asbreports.in") or "https://api.asbreports.in").rstrip("/")

ALLOWED_RAW = _get_secret("ALLOWED_FEATURES", "") or ""
ALLOWED = set(part.strip() for part in ALLOWED_RAW.split(",") if part.strip())

AI_TIMEOUT_SECS = int(_get_secret("AI_TIMEOUT", "300"))
DEFAULT_TIMEOUT_SECS = int(_get_secret("AI_TIMEOUT", "300"))

DOB_MIN = date(1900, 1, 1)
DOB_MAX = date.today()
TRIANGLE_IMG_WIDTH = 360

DEBUG_MODE = False


# ──────────────────────────────────────────────────────────────────────────────
# Robust HTTP session with retries (idempotent GETs only)
# ──────────────────────────────────────────────────────────────────────────────
def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


SESSION = _session()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _fmt_dob(d: date) -> str:
    return d.strftime("%d-%m-%Y")


def _fmt_day(d: date) -> str:
    return d.strftime("%d-%m-%Y")


def _parse_ddmmyyyy(s: str) -> date | None:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d-%m-%Y").date()
    except Exception:
        return None


def _params(**kw) -> Dict[str, Any]:
    return {k: v for k, v in kw.items() if v is not None}


@st.cache_data(ttl=300, show_spinner=False)
def api_get_cached(api_base: str, path: str, params: Optional[dict], timeout: int) -> Dict[str, Any] | bytes:
    base = (api_base or "").rstrip("/")
    url = f"{base}{path}"
    # Use tuple for explicit (connect, read) timeouts
    t = (10, timeout)
    r = SESSION.get(url, params=params, timeout=t)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if "application/json" in ctype:
        return r.json()
    return r.content


def api_get_json(path: str, params: Optional[dict] = None):
    timeout = DEFAULT_TIMEOUT_SECS
    try:
        res = api_get_cached(API_BASE, path, params, timeout)
        if isinstance(res, dict):
            return res
        if DEBUG_MODE:
            st.error(f"Expected JSON but got {type(res).__name__}")
        else:
            st.error("⚠️ We received an unexpected response format from the server.")
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"GET {path} failed: {e}")
        else:
            st.error("⚠️ Unable to reach the server. Please check your connection or try again later.")
    return None


def api_get_bytes(path: str, params: Optional[dict] = None) -> bytes | None:
    timeout = DEFAULT_TIMEOUT_SECS
    try:
        res = api_get_cached(API_BASE, path, params, timeout)
        if isinstance(res, (bytes, bytearray)):
            return res
        if DEBUG_MODE:
            st.error(f"Expected bytes but got {type(res).__name__}")
        else:
            st.error("⚠️ The document could not be retrieved in the expected format.")
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"GET {path} failed: {e}")
        else:
            st.error("⚠️ Failed to download the requested file. Please try again.")
    return None


def api_post_json(path: str, payload: dict, headers: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT_SECS):
    url = f"{API_BASE}{path}"
    try:
        h = headers.copy() if headers else {}
        t = (10, timeout)
        r = requests.post(url, json=payload, headers=h, timeout=t)

        if r.status_code >= 400:
            if r.status_code in {401, 403}:
                st.error("🔐 Your session has expired. Please log in again.")
            else:
                if DEBUG_MODE:
                    st.error(f"POST {path} failed ({r.status_code})")
                    try:
                        st.json(r.json())
                    except:
                        st.write(r.text)
                else:
                    st.error("⚠️ Request failed. Please check your input and try again.")
            return None

        return r.json()
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"POST {path} failed: {e}")
        else:
            st.error("⚠️ Network error. Please check your internet connection.")
        return None


def api_get_json_with_headers(path: str, headers: dict, timeout: int = DEFAULT_TIMEOUT_SECS):
    url = f"{API_BASE}{path}"
    try:
        t = (10, timeout)
        r = requests.get(url, headers=headers, timeout=t)

        if r.status_code >= 400:
            if r.status_code in {401, 403}:
                st.error("🔐 Access denied. Please log in again.")
            else:
                if DEBUG_MODE:
                    st.error(f"GET {path} failed ({r.status_code})")
                else:
                    st.error("⚠️ Unable to sync data with the server.")
            return None

        return r.json()
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"GET {path} failed: {e}")
        else:
            st.error("⚠️ Connection lost. Please refresh the page.")
        return None


def _download_button_bytes(label: str, data: bytes, file_name: str, mime: str):
    if data:
        st.download_button(label, data=data, file_name=file_name, mime=mime)


def _exp_json(label: str, data):
    with st.expander(label, expanded=False):
        st.json(data)


def _format_ai_interpretation(interp: str) -> str:
    if not isinstance(interp, str):
        return ""
    lines = [ln.strip() for ln in interp.splitlines() if ln.strip()]
    if not lines:
        return ""
    has_bullet = any(ln.startswith("•") for ln in lines)
    if not has_bullet:
        return interp.strip()

    md_lines = []
    for ln in lines:
        if ln.startswith("•"):
            content = ln.lstrip("•").strip()
            md_lines.append(f"- {content}")
        else:
            if md_lines:
                md_lines.append("")
            md_lines.append(ln)
    return "\n".join(md_lines).strip()


def _ai_block(title: str, path: str, debug: bool = False, **params):
    st.subheader(title)
    clean_params = _params(**params)

    if debug:
        from urllib.parse import urlencode
        qs = urlencode(clean_params, doseq=True)
        st.code(f"GET {API_BASE}{path}?{qs}", language="bash")

    j = api_get_json(path, clean_params)
    if not j:
        st.info("ℹ️ The interpretation is taking a bit longer than usual. Please refresh the section or try again in a moment.")
        return

    interp = j.get("interpretation")
    if isinstance(interp, str) and interp.strip():
        formatted = _format_ai_interpretation(interp)
        st.markdown(formatted)
    else:
        st.info("ℹ️ No AI interpretation returned.")

    if debug:
        _exp_json("AI raw JSON", j)


# ──────────────────────────────────────────────────────────────────────────────
# Auth state + helpers
# ──────────────────────────────────────────────────────────────────────────────
E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")


def _is_valid_phone_e164(phone: str) -> bool:
    phone = (phone or "").strip().replace(" ", "")
    return bool(E164_RE.match(phone))


if "auth" not in st.session_state:
    st.session_state["auth"] = {"token": None, "user": None}

def _set_auth(tok: str | None, user: Optional[dict]):
    st.session_state["auth"]["token"] = tok
    st.session_state["auth"]["user"] = user


def _handle_sso_query_params():
    """
    Check for sso_token in URL query params.
    Example: ?sso_token=eyJhbG...
    """
    # 1. Look for sso_token
    sso_token = st.query_params.get("sso_token")
    if not sso_token:
        return

    # 2. If already logged in with same token, just clear and ignore
    current_token = st.session_state.get("auth", {}).get("token")
    if current_token == sso_token:
        # Just clear the URL param to keep it clean
        query_params = st.query_params.to_dict()
        if "sso_token" in query_params:
            del query_params["sso_token"]
            st.query_params.clear()
            for k, v in query_params.items():
                st.query_params[k] = v
        return

    # 3. Validate token with backend
    me = api_get_json_with_headers("/api/auth/me", headers={"X-Auth-Token": sso_token})
    if me and me.get("success"):
        u = me.get("user") or {}
        _set_auth(sso_token, u)
        st.success(f"SSO: Welcome back, {u.get('name', 'User')}!")
        
        # 4. Clear the query parameter to avoid infinite refresh or leakage
        query_params = st.query_params.to_dict()
        if "sso_token" in query_params:
            del query_params["sso_token"]
            st.query_params.clear()
            for k, v in query_params.items():
                st.query_params[k] = v
        
        st.rerun()
    else:
        if DEBUG_MODE:
            st.error("SSO Login failed. The token may be expired or invalid.")
        else:
            st.error("🔐 SSO Login failed. Please log in manually or try again from the marketplace.")





# ──────────────────────────────────────────────────────────────────────────────
# Profile completeness
# ──────────────────────────────────────────────────────────────────────────────
REQUIRED_PROFILE_FIELDS = ("name", "phone", "dob", "gender")


def _missing_profile_fields(user: dict) -> list[str]:
    missing = []
    for k in REQUIRED_PROFILE_FIELDS:
        v = (user or {}).get(k)
        if v is None:
            missing.append(k)
            continue
        if isinstance(v, str) and not v.strip():
            missing.append(k)

    if "dob" not in missing and isinstance(user.get("dob"), str):
        try:
            datetime.strptime(user["dob"], "%d-%m-%Y")
        except Exception:
            missing.append("dob")

    if "gender" not in missing and isinstance(user.get("gender"), str):
        if user["gender"].strip().lower() not in {"male", "female", "other"}:
            missing.append("gender")

    return sorted(set(missing))


def _profile_ready() -> bool:
    user = st.session_state.get("auth", {}).get("user") or {}
    return len(_missing_profile_fields(user)) == 0


def _require_profile_or_block(feature_title: str) -> bool:
    user = st.session_state.get("auth", {}).get("user") or {}
    missing = _missing_profile_fields(user)
    if missing:
        st.warning(
            f"Complete your profile to use **{feature_title}**.\n\n"
            f"Missing: {', '.join(missing)}"
        )
        st.info("Go to **Profile** and complete DOB & Gender once.")
        return False
    return True


def _profile_dob_date() -> date:
    user = st.session_state.get("auth", {}).get("user") or {}
    return datetime.strptime(user["dob"], "%d-%m-%Y").date()


def _profile_gender() -> str:
    user = st.session_state.get("auth", {}).get("user") or {}
    return str(user.get("gender", "") or "").strip().lower()


def _profile_name() -> str:
    user = st.session_state.get("auth", {}).get("user") or {}
    return str(user.get("name", "") or "").strip()


def _profile_phone() -> str:
    user = st.session_state.get("auth", {}).get("user") or {}
    return str(user.get("phone", "") or "").strip()


def _default_dob() -> date:
    user = st.session_state.get("auth", {}).get("user") or {}
    if user and isinstance(user.get("dob"), str):
        try:
            return datetime.strptime(user["dob"], "%d-%m-%Y").date()
        except Exception:
            pass
    return date(2001, 1, 1)


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────
page: Optional[str] = None

with st.sidebar:
    st.title("ASB")
    st.markdown("---")

    auth_state = st.session_state["auth"]
    user = auth_state.get("user")

    if user:
        safe_name = str((user or {}).get("name") or "").strip() or "User"
        st.markdown(f"### 👋 Hi, {safe_name}")
        st.caption(f"📞 Phone: {str((user or {}).get('phone') or '-')}")
        st.caption(f"📅 DOB: {str((user or {}).get('dob') or '-')}")

        g = str((user or {}).get("gender") or "").strip()
        if g:
            st.caption(f"⚧ Gender: {g.title()}")

        missing = _missing_profile_fields(user)
        if missing:
            st.error(f"Profile incomplete: {', '.join(missing)}")
            st.caption("Complete profile to unlock all features.")

        sections_all = [
            "Profile",
            "Personality Traits",
            "Profession",
            "Relationship",
            "Time Cycles",
            "Health",
            "Overall Summary / PDF",
            "Consult & Remedies",
        ]
        gate_map = {
            "profile": "Profile",
            "single": "Personality Traits",
            "profession": "Profession",
            "relationship": "Relationship",
            "yearly": "Time Cycles",
            "monthly": "Time Cycles",
            "daily": "Time Cycles",
            "health": "Health",
            "ai": "Overall Summary / PDF",
            "consult": "Consult & Remedies",
        }

        if ALLOWED:
            allowed_labels = [gate_map[k] for k in gate_map if k in ALLOWED]
            seen = set()
            sections = []
            for lbl in allowed_labels:
                if lbl not in seen:
                    seen.add(lbl)
                    sections.append(lbl)
            sections = sections or sections_all
        else:
            sections = sections_all

        if missing:
            sections = ["Profile"]

        page = st.radio("Sections", sections, index=0)

        st.markdown("---")
        st.markdown(
            """
            ### ⚠️ Disclaimer  
            This numerology guidance is for  
            **educational & self-reflection purposes only**.  
            It is **not a substitute** for medical, legal,  
            financial or professional advice.  
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        if st.button("Logout"):
            _set_auth(None, None)
            st.rerun()
    else:
        st.subheader("Welcome")
        st.write("Please **login or register** to use the ASB Numerology platform.")
        st.markdown("---")
        st.markdown(
            """
            ### ⚠️ Disclaimer  
            This numerology guidance is for  
            **educational & self-reflection purposes only**.  
            It is **not a substitute** for medical, legal,  
            financial or professional advice.  
            """,
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Auth page (OTP)
# ──────────────────────────────────────────────────────────────────────────────
def page_auth():
    st.title("🔐 ASB Numerology — Login / Register (OTP)")
    st.caption("Use the same mobile number you use on ASBCrystal. This is Single Sign-On (SSO).")
    st.markdown("---")

    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "Login"
    if "login_otp_sent" not in st.session_state:
        st.session_state["login_otp_sent"] = False
    if "reg_otp_sent" not in st.session_state:
        st.session_state["reg_otp_sent"] = False

    mode = st.radio("Choose:", ["Login", "Register"], horizontal=True, key="auth_mode")
    st.markdown("---")

    if mode == "Login":
        st.subheader("Login with OTP")
        login_phone = st.text_input(
            "Phone (E.164 format)",
            key="login_phone_main",
            placeholder="+919999999999",
            help="Example: +919999999999",
        )

        if login_phone.strip() and not _is_valid_phone_e164(login_phone):
            st.error("Phone must include country code like +919999999999 (no spaces).")

        phone_ok = _is_valid_phone_e164(login_phone)

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Send OTP", type="primary", disabled=(not phone_ok)):
                res = api_post_json("/api/auth/send-otp", {"identifier": login_phone.strip()})
                if res is not None:
                    st.session_state["login_otp_sent"] = True
                    st.success("OTP sent!")

        if st.session_state["login_otp_sent"]:
            otp = st.text_input("Enter OTP", key="login_otp_code", placeholder="123456")
            with c2:
                if st.button("Verify OTP", type="primary", disabled=(not (phone_ok and otp.strip()))):
                    v = api_post_json(
                        "/api/auth/verify-otp",
                        {"identifier": login_phone.strip(), "otp": otp.strip(), "code": otp.strip()},
                    )

                    # ✅ Accept both token formats (some backends use accessToken)
                    token_value = None
                    if isinstance(v, dict):
                        token_value = v.get("token") or v.get("accessToken")

                    if token_value:
                        me = api_get_json_with_headers("/api/auth/me", headers={"X-Auth-Token": token_value})
                        if me and me.get("success"):
                            u = me.get("user") or {}
                            _set_auth(token_value, u)
                            st.session_state["login_otp_sent"] = False
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error("OTP verified but /api/auth/me failed.")
                    else:
                        st.error("OTP verification failed (no token returned).")

    else:
        st.subheader("Register with OTP (Complete Profile)")
        st.caption("Registration here is only for completing profile. Login is still OTP-based SSO.")

        col1, col2 = st.columns(2)
        with col1:
            reg_name = st.text_input("Full Name", key="reg_name_main")
            reg_phone = st.text_input(
                "Phone (E.164 format)",
                key="reg_phone_main",
                placeholder="+919999999999",
                help="Example: +919999999999",
            )
            if reg_phone.strip() and not _is_valid_phone_e164(reg_phone):
                st.error("Phone must include country code like +919999999999 (no spaces).")

        with col2:
            reg_dob = st.date_input(
                "DOB",
                value=date.today(),
                min_value=DOB_MIN,
                max_value=DOB_MAX,
                format="DD-MM-YYYY",
                key="reg_dob_main",
            )
            reg_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0, key="reg_gender_main")

        phone_ok = _is_valid_phone_e164(reg_phone)
        can_send = bool(reg_name.strip()) and phone_ok

        c1, c2 = st.columns([1, 1])
        with c1:
            # ✅ FIX: was /auth/send-otp (wrong). Must be /api/auth/send-otp
            if st.button("Send OTP", type="primary", key="reg_send_otp", disabled=(not can_send)):
                res = api_post_json("/api/auth/send-otp", {"identifier": reg_phone.strip()})
                if res is not None:
                    st.session_state["reg_otp_sent"] = True
                    st.success("OTP sent!")

        if st.session_state["reg_otp_sent"]:
            reg_otp = st.text_input("Enter OTP", key="reg_otp_code", placeholder="123456")

            with c2:
                if st.button(
                    "Verify & Save Profile",
                    type="primary",
                    key="reg_verify_btn",
                    disabled=(not (can_send and reg_otp.strip())),
                ):
                    # ✅ FIX: was /auth/verify-otp (wrong). Must be /api/auth/verify-otp
                    v = api_post_json("/api/auth/verify-otp", {"identifier": reg_phone.strip(), "otp": reg_otp.strip()})

                    token_value = None
                    if isinstance(v, dict):
                        token_value = v.get("token") or v.get("accessToken")

                    if token_value:
                        prof_payload = {
                            "dob": _fmt_dob(reg_dob),
                            "gender": reg_gender.lower(),
                            "name": reg_name.strip(),
                        }
                        saved = api_post_json("/api/auth/complete-profile", prof_payload, headers={"X-Auth-Token": token_value})
                        if not saved:
                            st.error("OTP verified but profile save failed.")
                            return

                        me = api_get_json_with_headers("/api/auth/me", headers={"X-Auth-Token": token_value})
                        if me and me.get("success"):
                            u = me.get("user") or {}
                            _set_auth(token_value, u)
                            st.session_state["reg_otp_sent"] = False
                            st.success("🎉 Account verified & logged in successfully!")
                            st.rerun()
                        else:
                            if DEBUG_MODE:
                                st.error("Registered but /api/auth/me failed.")
                            else:
                                st.error("⚠️ Log in failed after verification. Please try logging in manually.")
                    else:
                        if DEBUG_MODE:
                            st.error("OTP verification failed (no token returned).")
                        else:
                            st.error("❌ Invalid OTP. Please check the code and try again.")


# ──────────────────────────────────────────────────────────────────────────────
# (Your remaining pages are unchanged below)
# ──────────────────────────────────────────────────────────────────────────────
def _pill_html(text: str) -> str:
    safe = (text or "").replace("<", "&lt;").replace(">", "&gt;")
    return f'<span class="asb-pill">{safe}</span>'


def _render_quick_bulletins(dob_str: str, gender: str):
    personality = api_get_json("/api/numerology/mystical-triangle.report.json", {"dob": dob_str}) or {}
    prof = api_get_json("/api/numerology/profession.report.json", {"dob": dob_str}) or {}
    daily = api_get_json("/api/numerology/features/daily-triangle.report.json", {"dob": dob_str}) or {}
    health = api_get_json("/api/numerology/health-triangle.report.json", {"dob": dob_str, "gender": gender}) or {}

    mb = (personality.get("mulank_bhagyank") or {})
    mulank = mb.get("mulank")
    bhagyank = mb.get("bhagyank")

    interp_core = ((personality.get("interpretations") or {}).get("core") or {})
    g_core = interp_core.get("G") if isinstance(interp_core.get("G"), dict) else {}
    g_val = g_core.get("value") if isinstance(g_core, dict) else None
    g_mean = g_core.get("meaning") if isinstance(g_core, dict) else None

    ef_core = interp_core.get("EF_core") if isinstance(interp_core.get("EF_core"), dict) else {}
    ef_val = ef_core.get("value") if isinstance(ef_core, dict) else None

    prof_data = (prof.get("profession") or {})
    prof_rating = prof_data.get("rating_short") or prof_data.get("rating_text") or "-"
    prof_list = prof_data.get("professions") or []
    prof_top = prof_list[:3] if isinstance(prof_list, list) else []

    panels = (daily.get("panels") or {}) if isinstance(daily, dict) else {}
    combined = (panels.get("combined") or {}) if isinstance(panels.get("combined"), dict) else {}
    c_core = (combined.get("core") or {}) if isinstance(combined.get("core"), dict) else {}
    today_g = c_core.get("G", {}).get("value") if isinstance(c_core.get("G"), dict) else c_core.get("G")

    special = (combined.get("special_notes") or {}) if isinstance(combined.get("special_notes"), dict) else {}
    tags = special.get("tags") or []
    tags = [t for t in tags if isinstance(t, str)][:6]

    sections = (health.get("sections") or {}) if isinstance(health, dict) else {}
    core_health = (sections.get("core_health") or {}) if isinstance(sections.get("core_health"), dict) else {}
    vital = (core_health.get("Vital Energy (G)") or {}) if isinstance(core_health.get("Vital Energy (G)"), dict) else {}
    vital_g = vital.get("value")
    vital_mean = vital.get("meaning")

    st.markdown("### ✨ Quick Bulletins")

    prof_pills = "".join([_pill_html(p) for p in prof_top]) if prof_top else _pill_html("No suggestions")
    tag_pills = "".join([_pill_html(t.replace("_", " ")) for t in tags]) if tags else _pill_html("No special signals")

    card1 = f"""
<div class="asb-card">
  <h4>🧠 Personality</h4>
  <div class="asb-kv"><span>Mulank</span><b>{mulank if mulank is not None else "-"}</b></div>
  <div class="asb-kv"><span>Bhagyank</span><b>{bhagyank if bhagyank is not None else "-"}</b></div>
  <div class="asb-kv"><span>Core (G)</span><b>{g_val if g_val is not None else "-"}</b></div>
  <div class="asb-kv"><span>Core Pair (EF)</span><b>{ef_val if ef_val is not None else "-"}</b></div>
  <div class="asb-muted" style="margin-top:6px;">{(g_mean or "—")}</div>
</div>
"""
    card2 = f"""
<div class="asb-card">
  <h4>💼 Profession</h4>
  <div class="asb-kv"><span>Rating</span><b>{prof_rating}</b></div>
  <div class="asb-muted" style="margin-top:6px;">Top matches</div>
  <div class="asb-pillrow">{prof_pills}</div>
</div>
"""
    card3 = f"""
<div class="asb-card">
  <h4>🕒 Today</h4>
  <div class="asb-kv"><span>Today Core (G)</span><b>{today_g if today_g is not None else "-"}</b></div>
  <div class="asb-muted" style="margin-top:6px;">Signals</div>
  <div class="asb-pillrow">{tag_pills}</div>
</div>
"""
    card4 = f"""
<div class="asb-card">
  <h4>🩺 Health</h4>
  <div class="asb-kv"><span>Vital (G)</span><b>{vital_g if vital_g is not None else "-"}</b></div>
  <div class="asb-muted" style="margin-top:6px;">{(vital_mean or "—")}</div>
</div>
"""

    st.markdown(f'<div class="asb-cards">{card1}{card2}{card3}{card4}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Pages
# ──────────────────────────────────────────────────────────────────────────────
def page_profile():
    st.header("👤 Profile")

    token = st.session_state.get("auth", {}).get("token")
    user = st.session_state.get("auth", {}).get("user") or {}

    safe_name = str((user or {}).get("name") or "User").strip() or "User"
    st.markdown(f"### {safe_name}")
    st.write(f"**Phone:** {str((user or {}).get('phone') or '-')}")
    st.write(f"**DOB:** {str((user or {}).get('dob') or '-')}")
    g_show = str((user or {}).get("gender") or "").strip()
    st.write(f"**Gender:** {g_show.title() if g_show else '-'}")

    if _profile_ready():
        dob_str = _fmt_dob(_profile_dob_date())
        gender = _profile_gender()
        st.markdown("---")
        with st.spinner("Building quick bulletins…"):
            _render_quick_bulletins(dob_str, gender)
    else:
        st.markdown("---")
        st.caption("✨ Quick Bulletins will appear after you save DOB & Gender.")

    missing = _missing_profile_fields(user)
    if missing:
        st.warning(f"Profile incomplete: {', '.join(missing)}")
        st.info("Fill these details once — they will be stored in the main Users DB (SSO).")

        name_default = str((user or {}).get("name") or "").strip()
        gender_default = str((user or {}).get("gender") or "").strip().lower()
        gender_list = ["male", "female", "other"]
        gender_index = gender_list.index(gender_default) if gender_default in gender_list else 0

        with st.form("complete_profile_form"):
            name = st.text_input("Full Name", value=name_default)
            dob = st.date_input("DOB", value=_default_dob(), min_value=DOB_MIN, max_value=DOB_MAX, format="DD-MM-YYYY")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=gender_index)
            submitted = st.form_submit_button("Save Profile", type="primary")

        if submitted:
            if not token:
                st.error("Missing auth token. Please login again.")
                return

            payload = {
                "name": name.strip(),
                "dob": _fmt_dob(dob),
                "gender": gender.lower(),
            }
            saved = api_post_json("/api/auth/complete-profile", payload, headers={"X-Auth-Token": token})
            if saved and saved.get("success"):
                me = api_get_json_with_headers("/api/auth/me", headers={"X-Auth-Token": token})
                if me and me.get("success"):
                    u = me.get("user") or {}
                    _set_auth(token, u)
                    st.success("Profile updated!")
                    st.rerun()
                else:
                    st.error("Saved profile, but failed to refresh /auth/me.")


def page_single_person():
    st.header("Personality Traits")
    if not _require_profile_or_block("Personality Traits"):
        return

    col1, _ = st.columns([1, 2])
    with col1:
        dob = st.date_input("DOB", value=_profile_dob_date(), min_value=DOB_MIN, max_value=DOB_MAX,
                            format="DD-MM-YYYY", disabled=True)
        dob_str = _fmt_dob(dob)
        st.caption(f"Formatted: {dob_str}")
        run = st.button("Generate", type="primary")

    if not run:
        return

    png = api_get_bytes("/api/numerology/mystical-triangle.png", {"dob": dob_str})
    if png:
        st.image(png, caption=f"Triangle — DOB {dob_str}", width=TRIANGLE_IMG_WIDTH, use_container_width=False)

    st.markdown("---")
    st.subheader("Mulank & Bhagyank Profile")
    mb = api_get_json("/api/numerology/mulank-bhagyank.profile.json", {"dob": dob_str})
    if mb:
        mulank = mb.get("mulank")
        bhagyank = mb.get("bhagyank")
        pair = mb.get("pair") or {}
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Mulank", mulank if mulank is not None else "-")
        with c2:
            st.metric("Bhagyank", bhagyank if bhagyank is not None else "-")
        with c3:
            st.metric("Pair Rating", pair.get("rating_label") or "-")
        rating_meaning = pair.get("rating_meaning")
        if rating_meaning:
            st.caption(f"*Rating meaning: {rating_meaning} combination*")
    else:
        st.info("Mulank / Bhagyank profile not available for this DOB.")

    st.markdown("---")
    _ai_block("Personality Interpretation", "/api/ai/summary", debug=DEBUG_MODE, dob=dob_str)

    st.markdown("---")
    st.subheader("SWOT Analysis")
    swot_json = api_get_json("/api/ai/swot.ai.json", {"dob": dob_str})
    if not swot_json:
        # Error already handled by api_get_json
        return

    swot = swot_json.get("swot", {})
    colS, colW = st.columns(2)
    colO, colT = st.columns(2)

    with colS:
        st.markdown("### Strengths")
        for item in swot.get("Strengths", []):
            st.markdown(f"- {item}")

    with colW:
        st.markdown("### Weaknesses")
        for item in swot.get("Weaknesses", []):
            st.markdown(f"- {item}")

    with colO:
        st.markdown("### Opportunities")
        for item in swot.get("Opportunities", []):
            st.markdown(f"- {item}")

    with colT:
        st.markdown("### Threats")
        threats = swot.get("Threats", [])
        if threats:
            for item in threats:
                st.markdown(f"- {item}")
        else:
            st.markdown("*No major threats.*")


def page_profession():
    st.header("Profession / Career Guidance")
    if not _require_profile_or_block("Profession"):
        return

    col1, _ = st.columns([1, 2])
    with col1:
        dob = st.date_input("DOB", value=_profile_dob_date(), min_value=DOB_MIN, max_value=DOB_MAX,
                            format="DD-MM-YYYY", disabled=True)
        dob_str = _fmt_dob(dob)
        st.caption(f"Formatted: {dob_str}")
        run = st.button("Generate", type="primary")

    if not run:
        return

    png = api_get_bytes("/api/numerology/mystical-triangle.png", {"dob": dob_str})
    if png:
        st.image(png, caption=f"Triangle — DOB {dob_str}", width=TRIANGLE_IMG_WIDTH, use_container_width=False)

    st.markdown("---")
    prof = api_get_json("/api/numerology/profession.report.json", {"dob": dob_str})
    if prof:
        st.subheader("Mulank–Bhagyank Profession Profile")
        pdata = prof.get("profession", {}) or {}
        professions = pdata.get("professions") or []

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Mulank", prof.get("mulank") if prof.get("mulank") is not None else "-")
        with c2:
            st.metric("Bhagyank", prof.get("bhagyank") if prof.get("bhagyank") is not None else "-")
        with c3:
            st.metric("Career Rating", pdata.get("rating_short") or pdata.get("rating_text") or "-")

        if pdata.get("remark"):
            st.info(pdata["remark"])

        if professions:
            st.markdown("### Suitable Professions / Domains")
            for p in professions:
                st.markdown(f"- {p}")
    else:
        st.warning("⚠ Profession data not available.")

    st.markdown("---")
    _ai_block("Profession/Career Interpretation", "/api/ai/profession.ai.json", debug=DEBUG_MODE, dob=dob_str)


def page_relationship():
    st.header("Relationship")
    if not _require_profile_or_block("Relationship"):
        return

    c1, c2 = st.columns(2)
    with c1:
        left = st.date_input("Your DOB", value=_profile_dob_date(), min_value=DOB_MIN, max_value=DOB_MAX,
                             format="DD-MM-YYYY", disabled=True)
    with c2:
        partner_date = st.date_input("Partner DOB", value=date.today(), min_value=DOB_MIN, max_value=DOB_MAX,
                                     format="DD-MM-YYYY")
        partner_raw = _fmt_dob(partner_date)

    right_date = _parse_ddmmyyyy(partner_raw)
    partner_ok = bool(partner_raw.strip()) and (right_date is not None)

    if st.button("Generate", type="primary", disabled=(not partner_ok)):
        left_str = _fmt_dob(left)
        right_str = _fmt_dob(right_date)  # type: ignore[arg-type]

        png = api_get_bytes("/api/numerology/mystical-triangle-triptych.png", {"left": left_str, "right": right_str})
        if png:
            st.image(png, caption="Relationship Triptych", width=TRIANGLE_IMG_WIDTH, use_container_width=False)

        st.markdown("---")
        _ai_block("Relationship Interpretation", "/api/ai/relationship-triangle.ai.json",
                  debug=DEBUG_MODE, left=left_str, right=right_str)


def page_time_cycles():
    st.header("Time Cycles — Yearly / Monthly / Daily")
    if not _require_profile_or_block("Time Cycles"):
        return

    dob_str = _fmt_dob(_profile_dob_date())

    tab_y, tab_m, tab_d = st.tabs(["Yearly", "Monthly", "Daily"])

    with tab_y:
        year_y = st.number_input("Target Year", value=date.today().year, min_value=1900, max_value=3000, step=1)
        if st.button("Generate Yearly", type="primary"):
            png = api_get_bytes("/api/numerology/yearly-triptych.png", {"dob": dob_str, "year": int(year_y)})
            if png:
                st.image(png, caption="Yearly Triptych", width=TRIANGLE_IMG_WIDTH, use_container_width=False)
            st.markdown("---")
            _ai_block("Yearly Prediction", "/api/ai/yearly-prediction.ai.json", debug=DEBUG_MODE, dob=dob_str, year=int(year_y))

    with tab_m:
        year_m = st.number_input("Target Year", value=date.today().year, min_value=1900, max_value=3000, step=1, key="tc_year_m")
        month_m = st.selectbox(
            "Target Month",
            options=list(range(1, 13)),
            index=date.today().month - 1,
            format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
            key="tc_month_m",
        )
        if st.button("Generate Monthly", type="primary"):
            png = api_get_bytes("/api/numerology/monthly-triptych.png", {"dob": dob_str, "year": int(year_m), "month": int(month_m)})
            if png:
                st.image(png, caption=f"Monthly Triptych — {datetime(int(year_m), month_m, 1).strftime('%B %Y')}",
                         width=TRIANGLE_IMG_WIDTH, use_container_width=False)
            st.markdown("---")
            _ai_block("Monthly Prediction", "/api/ai/monthly-prediction.ai.json", debug=DEBUG_MODE,
                      dob=dob_str, year=int(year_m), month=int(month_m))

    with tab_d:
        day = st.date_input("Day", value=date.today(), format="DD-MM-YYYY", key="tc_day")
        day_str = _fmt_day(day)
        if st.button("Generate Daily", type="primary"):
            png = api_get_bytes("/api/numerology/daily-triptych.png", {"dob": dob_str, "day": day_str})
            if png:
                st.image(png, caption=f"Daily Triptych — {day_str}", width=TRIANGLE_IMG_WIDTH, use_container_width=False)
            st.markdown("---")
            _ai_block("Daily Interpretation", "/api/ai/daily-interpretation.ai.json", debug=DEBUG_MODE, dob=dob_str, day=day_str)


def page_health():
    st.header("Health — Generic / Yearly / Monthly / Daily")
    if not _require_profile_or_block("Health"):
        return

    dob_str = _fmt_dob(_profile_dob_date())
    gender = _profile_gender()

    tab1, tab2, tab3, tab4 = st.tabs(["Generic", "Yearly", "Monthly", "Daily"])

    with tab1:
        if st.button("Generate Generic Health", type="primary"):
            png = api_get_bytes("/api/numerology/mystical-triangle.png", {"dob": dob_str})
            if png:
                st.image(png, caption=f"Triangle — DOB {dob_str}", width=TRIANGLE_IMG_WIDTH, use_container_width=False)
            st.markdown("---")
            _ai_block("Health Summary", "/api/ai/health-summary", debug=DEBUG_MODE, dob=dob_str, gender=gender)

    with tab2:
        year_y = st.number_input("Target Year", value=date.today().year, min_value=1900, max_value=3000, step=1, key="h_year")
        if st.button("Generate Yearly Health", type="primary"):
            _ai_block("Yearly Health Interpretation", "/api/ai/health/yearly.ai.json", debug=DEBUG_MODE,
                      dob=dob_str, year=int(year_y), gender=gender)

    with tab3:
        year_m = st.number_input("Target Year", value=date.today().year, min_value=1900, max_value=3000, step=1, key="h_year_m")
        month_m = st.selectbox(
            "Target Month",
            options=list(range(1, 13)),
            index=date.today().month - 1,
            format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
            key="h_month_m",
        )
        if st.button("Generate Monthly Health", type="primary"):
            _ai_block("Monthly Health Interpretation", "/api/ai/health/monthly.ai.json", debug=DEBUG_MODE,
                      dob=dob_str, year=int(year_m), month=int(month_m), gender=gender)

    with tab4:
        day = st.date_input("Day", value=date.today(), format="DD-MM-YYYY", key="h_day")
        day_str = _fmt_day(day)
        if st.button("Generate Daily Health", type="primary"):
            _ai_block("Daily Health Interpretation", "/api/ai/health/daily.ai.json", debug=DEBUG_MODE,
                      dob=dob_str, day=day_str, gender=gender)


def page_ai():
    st.header("Overall Summary / PDF")
    if not _require_profile_or_block("Overall Summary / PDF"):
        return

    name = st.text_input("Name", value=_profile_name(), disabled=True)
    mobile = st.text_input("Mobile Number", value=_profile_phone(), disabled=True)

    report_date = st.date_input("Report Date", value=date.today(), format="DD-MM-YYYY")

    dob_str = _fmt_dob(_profile_dob_date())
    gender = _profile_gender()

    c1, c2 = st.columns([1, 1])
    with c1:
        year = st.number_input("Year", value=date.today().year, min_value=1900, max_value=3000, step=1)
        month = st.selectbox(
            "Month",
            options=list(range(1, 13)),
            index=date.today().month - 1,
            format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
        )
        day = st.date_input("Day", value=date.today(), format="DD-MM-YYYY")
        include_images = True

    with c2:
        partner_dob_str = None
        partner_date = st.date_input("Partner DOB (optional)", value=date.today(), min_value=DOB_MIN, max_value=DOB_MAX, format="DD-MM-YYYY")
        add_partner = st.checkbox("Add Relationship section", value=False)
        if add_partner:
            partner_dob_str = _fmt_dob(partner_date)

    can_build = (not add_partner) or bool(partner_dob_str)

    if st.button("Build PDF", type="primary", disabled=(not can_build)):
        params = {
            "dob": dob_str,
            "name": name,
            "mobile": mobile,
            "report_date": _fmt_day(report_date),
            "year": int(year),
            "month": int(month),
            "day": _fmt_day(day),
            "gender": gender,
            "include_images": include_images,
            "partner": partner_dob_str if partner_dob_str else None,
        }
        pdf_bytes = api_get_bytes("/api/ai/master-report.pdf", _params(**params))
        _download_button_bytes("⬇️ Download PDF", pdf_bytes, f"ASB-Report-{name}.pdf", "application/pdf")


def page_consult():
    st.header("Consult & Remedies")
    st.markdown(
        """
If you’d like a **personalised consultation**, detailed **remedies plan**,  
or a deeper walkthrough of your ASB report, you can reach out below.
        """
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📞 Contact")
        st.markdown(
            """
**Name:** *ASB*  
**Mobile / WhatsApp:** `+91-9911500291`  
**Email:** `astroschoolbaba@gmail.com`  
            """
        )

    with col2:
        st.subheader("🕒 Consultation Slots")
        st.markdown(
            """
- Weekdays: *6:00 PM – 9:00 PM (IST)*  
- Weekends: *11:00 AM – 5:00 PM (IST)*  
            """
        )

    st.markdown("---")
    st.subheader("📌 What you can consult for")
    st.markdown(
        """
- Personal numerology & name corrections  
- Career & profession direction  
- Relationship insights  
- Health rhythm & lifestyle alignment  
- Time-cycle based planning (years / months / days)  
        """
    )

    st.info(
        "All guidance is numerology-based and intended for reflection and planning. "
        "It is not a substitute for medical, legal, or financial advice."
    )


# ──────────────────────────────────────────────────────────────────────────────
# Router / Entry
# ──────────────────────────────────────────────────────────────────────────────
_handle_sso_query_params()

auth_user = st.session_state.get("auth", {}).get("user")

if not auth_user:
    page_auth()
else:
    if not _profile_ready():
        page = "Profile"

    if page is None:
        page = "Profile"

    if page == "Profile":
        page_profile()
    elif page == "Personality Traits":
        page_single_person()
    elif page == "Profession":
        page_profession()
    elif page == "Relationship":
        page_relationship()
    elif page == "Time Cycles":
        page_time_cycles()
    elif page == "Health":
        page_health()
    elif page == "Overall Summary / PDF":
        page_ai()
    elif page == "Consult & Remedies":
        page_consult()
    else:
        page_profile()
