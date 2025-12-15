# DATASET DATASHEET — IrisVisionAI (v0.2)

## 1. Dataset Identity
- **Dataset Name:** CASIA-Iris-Interval  
- **Source:** CASIA Iris Image Database (Chinese Academy of Sciences)  
- **Modality:** Near-Infrared (NIR), grayscale  
- **Image Type:** Structural iris images  
- **Usage in Project:** Research-only, non-diagnostic structural iris analysis  

---

## 2. Dataset Scope (v0.2 Lock)
- **Primary Dataset:** CASIA-Iris-Interval  
- **Other CASIA Subsets:**  
  - CASIA-Iris-Lamp — Not used  
  - CASIA-Iris-Distance — Not used  
  - CASIA-Iris-Thousand — Not used  
  - CASIA-Iris-Syn — Not used  
- **External Datasets (PolyU, IITD, ND-GFI):** Archived, not used  
- **Dataset Status:** Frozen for v0.2  

---

## 3. Subjects
- **Total Subjects:** 249  
- **Subject Identifiers:** 001 – 249  
- **Eye Availability:**  
  - Some subjects contain both left and right eye images  
  - Some subjects contain only one eye  
- **Subject Independence:** Subjects are treated as independent units  

---

## 4. Images
- **Total Images:** 2639  
- **Image Format:** JPG  
- **Image Resolution:** 320 × 280 pixels  
- **Eye Types:**  
  - Left eye (L)  
  - Right eye (R)  
- **Images per Subject:** Variable  

---

## 5. Data Organization
- **Directory Structure:**
subject_id/

```bash
   ├──L/
   │  └── S1YYY L NN.jpg
   └──R/
      └── S1YYY R NN.jpg
```

- **File Naming Convention:**  
- `YYY` → Subject ID  
- `L / R` → Eye side  
- `NN` → Image index within subject-eye  
- **Raw Data Policy:**  
- No renaming performed  
- No image modification performed  

---

## 6. Quality Control (v0.2)
- **Corruption Check:** Performed programmatically  
- **Corrupt Images:** 0  
- **Blur & Occlusion Flags:**  
- Present in metadata  
- Conservatively applied  
- **Image Exclusion:** None at this stage  

---

## 7. Metadata
- **Metadata File:** `data/metadata/metadata.csv`  
- **Granularity:** One row per image  
- **Key Fields:**  
- Subject ID  
- Eye (L/R)  
- Image index  
- Resolution  
- Quality control flags  
- **Split Column:**  
- All values set to `unset`  
- Dataset not yet split  

---

## 8. Data Leakage Prevention
- **Split Strategy:** Subject-level (not image-level)  
- **Leakage Policy:**  
- A subject may appear in only one split  
- Left and right eyes of the same subject are treated as dependent  
- **Current Status:** No train/validation/test split applied  

---

## 9. Limitations
- No demographic metadata available  
- No acquisition timestamps available  
- Uneven distribution of images per subject  
- Dataset is not intended for medical diagnosis  

---

## 10. Version Status
- **v0.1:** Infrastructure & project setup — COMPLETE  
- **v0.2:** Dataset preparation & documentation — COMPLETE  
- **v0.3+:** Annotation, modeling, and interpretation — NOT STARTED  

---
