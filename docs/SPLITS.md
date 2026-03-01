# Dataset Split Protocol (v0.3)

This project uses subject-level splits.

- Unit of split: `subject_id`
- Ratios: 70% train / 15% validation / 15% test
- Seed: `69`
- Total subjects: `249`
- Leakage rule: a subject can appear in only one split

This split definition is frozen for the v0.3 line and should not be changed silently.
If we ever revise it, the change must be versioned and documented.
