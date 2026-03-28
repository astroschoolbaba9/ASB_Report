# Definitive Step-by-Step Deployment Guide: ASB Platform

This guide documents every configuration, command, and optimization applied to successfully deploy and synchronize the ASB platform on the Hostinger VPS.

---

## 1. Directory Structure & Owners
- **Base Path**: `/var/www/asb-main/`
- **Owner**: `root:www-data`
- **Python Virtual Env**: `/var/www/asb-main/venv/`

---

## 2. Environment Configuration (`.env`)
The `.env` file on the VPS contains critical overrides for production stability:
```bash
# Path: /var/www/asb-main/.env
ASB_API_BASE=https://api.asbreports.in
SECURITY_BYPASS=1
AI_TIMEOUT=300
ALLOWED_FEATURES=all
```

---

## 3. Nginx Tunneling & Timeouts (Definitive Config)
To resolve the **read timeout=60** and **504 Gateway Timeout** errors, Nginx was configured with 5-minute (300s) buffers.

**Configuration Path**: `/etc/nginx/sites-available/asbreports`
```nginx
server {
    server_name asbreports.in www.asbreports.in;

    location / {
        proxy_pass http://127.0.0.1:8502; # Streamlit Port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CRITICAL TIMEOUT FIXES
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/; # FastAPI Port
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```
**Command to apply**:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 4. Systemd Service Files
We use Systemd to ensure the apps run continuously and restart on failure.

### A. Backend Service (`asb_api.service`)
**Path**: `/etc/systemd/system/asb_api.service`
```ini
[Unit]
Description=ASB API Service (FastAPI)
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/asb-main
Environment="PATH=/var/www/asb-main/venv/bin"
EnvironmentFile=/var/www/asb-main/.env
ExecStart=/var/www/asb-main/venv/bin/uvicorn main_api:app --host 127.0.0.1 --port 8000 --proxy-headers
Restart=always

[Install]
WantedBy=multi-user.target
```

### B. Frontend Service (`asb_app.service`)
**Path**: `/etc/systemd/system/asb_app.service`
```ini
[Unit]
Description=ASB Streamlit App
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/asb-main
Environment="PATH=/var/www/asb-main/venv/bin"
EnvironmentFile=/var/www/asb-main/.env
ExecStart=/var/www/asb-main/venv/bin/streamlit run streamlit_app.py --server.port 8502 --server.address 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

**Commands to manage**:
```bash
sudo systemctl daemon-reload
sudo systemctl restart asb_app asb_api
sudo systemctl status asb_app asb_api
```

---

## 5. Explicit Code Optimization (Hot-Fixes)
To ensure the correct timeouts and branding, specific lines in the Python files were patched:

### A. Streamlit Timeout Hardcoding
In `streamlit_app.py`, we hardcoded the 300s value to ignore potential environment overrides:
```python
# Lines 257-258
AI_TIMEOUT_SECS = 300
DEFAULT_TIMEOUT_SECS = 300

# Tuple request enforcement
timeout = (10, 300) 
r = SESSION.get(url, params=params, timeout=timeout)
```

### B. SWOT Calculation Optimization
In `numerology/pdf.py`, the SWOT generation was optimized to avoid a redundant sequential AI call, derivation now happens from interpretation text.

---

## 6. Commands for Manual Path Synchronization
If you need to transfer files from local to VPS without `git push`:

1. **Convert file to Base64 locally**:
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes('streamlit_app.py'))
   ```
2. **Push to VPS**:
   ```bash
   echo "BASE64_STRING" | base64 -d > /var/www/asb-main/streamlit_app.py
   ```

---

## 7. Branding & Assets
The logo and favicon are correctly mapped:
- **Logo File**: `/var/www/asb-main/assets/asb.logo.jpg`
- **Logic**: Streamlit searches for this absolute path first to ensure the favicon displays correctly on the VPS.

---

## 8. Standard Local-to-VPS Workflow
Use these steps to push changes from your **Local Machine** and pull them on the **VPS**.

### A. On Local Machine (Windows)
1. **Navigate to Project**: Open PowerShell in `c:\Users\BHASKAR JOSHI\OneDrive\Desktop\ASB-main (1)\ASB-main`
2. **Add and Commit**:
   ```powershell
   git add .
   git commit -m "Describe your changes"
   ```
3. **Push to GitHub**:
   ```powershell
   git push origin main
   ```

### B. On VPS (Hostinger)
1. **Navigate to Project**:
   ```bash
   cd /var/www/asb-main
   ```
2. **Pull Changes**:
   ```bash
   git pull origin main
   ```
3. **Apply & Restart**:
   ```bash
   sudo systemctl restart asb_app asb_api
   ```

---

### Verification Checklist
- [x] `HTTP 200` on `https://asbreports.in`
- [x] `HTTP 200` on `https://api.asbreports.in`
- [x] Browser Tab shows ASB Favicon
- [x] PDF generation (Build PDF) completes without 60s timeout error.
