# SECURITY POLICY

## 1. Supported Versions
IrisAtlasAI is under active research development.  
Security updates or patches are provided **as needed**, not on a fixed release cycle.

| Version | Status |
|--------|--------|
| v1.x   | Supported (alpha) |
| v0.x   | Experimental |

---

## 2. Scope of Security Policy
This policy covers:
- code security  
- dependency vulnerabilities  
- data handling hygiene  
- safe use of AI models  
- misuse prevention  

This policy does **not** cover:
- privacy breaches resulting from misuse of external datasets  
- unauthorized use of CASIA-IrisV4 data  
- clinical misuse of outputs  

---

## 3. Reporting a Vulnerability

If you discover:
- a security flaw  
- a privacy weakness  
- an exploit  
- a misuse vector  

Please **do NOT create a public GitHub issue**.

Instead, report privately to:

📧 **vishal@praneon.com**  
(You can change this email to your preferred security inbox.)

Please include:
- description of vulnerability  
- reproduction steps  
- potential impact  
- suggested fix  

You will receive a response within **7–14 days**.

---

## 4. Responsible Use Requirements

Users must ensure:
- No clinical use  
- No biometric identification  
- No use in surveillance tools  
- No attempts to circumvent dataset licensing  
- No uploading private images to public forks  

This protects both users and the research community.

---

## 5. Dependency Security

This project uses:
- PyTorch  
- Ultralytics YOLO  
- nnU-Net  
- OpenCV  
- Python scientific libraries  

Users should:
- regularly update dependencies  
- avoid untrusted extensions  
- pin versions in `requirements.txt`  
- use virtual environments  

---

## 6. Model Output Safety

The VLM-based interpretation module may generate:
- hallucinated text  
- overconfident statements  
- ambiguous structural interpretations  

To prevent harm:
- All VLM outputs should be reviewed manually  
- VLM outputs must NEVER be used as medical guidance  
- Disclaimers must remain in place  

---

## 7. Security Best Practices for Developers

If modifying the codebase:
- Do not push raw datasets  
- Do not push trained models containing private data  
- Use `.gitignore` properly  
- Do not hardcode paths or keys  
- Avoid committing large binary files  
- Review contributions for unsafe features  

---

## 8. Enforcement

Violations of:
- dataset licensing  
- ethical guidelines  
- medical safety rules  
- misuse of pipeline for biometric identification  

may result in:
- blocked issues  
- denied pull requests  
- user reporting to GitHub Trust & Safety  

---

Thank you for helping keep **IrisAtlasAI** safe, ethical, and research-focused.
