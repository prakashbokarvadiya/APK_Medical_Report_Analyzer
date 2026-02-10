# 🏥 Medical Report Analyzer — Offline + TWA Setup Guide

---

## PART 1 — Offline Support (Service Worker)

### Step 1: Files place karo

| File | Kahan rakhna hai |
|------|-----------------|
| `sw.js` | `static/` folder me |
| `offline.html` | `templates/` folder me |
| `assetlinks.json` | `static/` folder me |

```
project/
├── app.py
├── static/
│   ├── sw.js               ✅ yahan
│   ├── assetlinks.json     ✅ yahan
│   └── icons/
│       ├── icon-192.png
│       └── icon-512.png
└── templates/
    ├── index.html
    └── offline.html        ✅ yahan
```

---

### Step 2: app.py me 3 routes add karo

`app_patch.py` file ke teeno routes apne `app.py` me paste karo,
`if __name__ == '__main__':` line se bilkul pehle.

---

### Step 3: Base template me SW register karo

Apne main HTML template (`index.html` / `base.html`) ke
`</body>` tag se pehle `sw_register_snippet.html` ka content paste karo.

---

### Step 4: sw.js me apne actual static paths update karo

```js
// sw.js me ye section update karo:
const STATIC_ASSETS = [
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/css/main.css',    // ← apni CSS
  '/static/js/main.js',      // ← apna JS
];
```

---

### Test karo

1. Chrome DevTools → Application → Service Workers
2. "Offline" checkbox tick karo
3. Page refresh karo — offline.html dikhni chahiye
4. Uncheck karo → automatically redirect ho jaata hai home par

---

---

## PART 2 — URL Bar Hide (TWA + assetlinks.json)

### Step 1: SHA-256 fingerprint nikalo

Play Console pe apni release ke baad fingerprint milta hai.
Ya apni keystore se:

```bash
keytool -list -v -keystore your-release-key.jks \
  -alias your-alias -storepass yourpassword
```

Output me `SHA256:` wali line copy karo (colons ke saath).

### Step 2: assetlinks.json update karo

```json
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.onrender.apk_medical_report_analyzer.twa",
      "sha256_cert_fingerprints": [
        "AB:CD:EF:12:34:56:..."   ← apna actual fingerprint
      ]
    }
  }
]
```

**`package_name`** = wahi jo tumne Android project me use kiya hai.

### Step 3: Verify karo ki route accessible hai

Browser me open karo:
```
https://yourdomain.com/.well-known/assetlinks.json
```
JSON response aana chahiye ✅

### Step 4: Google ka verification tool use karo

```
https://digitalassetlinks.googleapis.com/v1/statements:list
  ?source.web.site=https://yourdomain.com
  &relation=delegate_permission/common.handle_all_urls
```

`matched: true` aana chahiye ✅

### Step 5: Bubblewrap se TWA build karo (easiest method)

```bash
npm install -g @bubblewrap/cli

bubblewrap init --manifest https://yourdomain.com/static/manifest.json
# package name, keystore details fill karo

bubblewrap build
# .apk / .aab generate hoga
```

---

## Summary

```
Offline Support Flow:
User opens app → SW registered → Assets cached
User loses internet → Page request fails → SW serves /offline
User regains internet → JS detects online → Auto-redirect to /

URL Bar Flow:
TWA app installed → Opens domain → Chrome checks /.well-known/assetlinks.json
fingerprint matches → Full-screen mode → No address bar shown
```

---

## Checklist

- [ ] sw.js `static/` me rakha
- [ ] offline.html `templates/` me rakha  
- [ ] assetlinks.json `static/` me rakha
- [ ] 3 routes app.py me add kiye
- [ ] SW register snippet HTML me add kiya
- [ ] static paths sw.js me update kiye
- [ ] SHA-256 fingerprint assetlinks.json me fill kiya
- [ ] `/.well-known/assetlinks.json` URL accessible hai
- [ ] Bubblewrap se TWA build kiya
- [ ] Play Console me app upload kiya
