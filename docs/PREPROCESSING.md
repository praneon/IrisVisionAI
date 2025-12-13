# Preprocessing & Augmentation

## Preprocessing Steps
1. Convert to grayscale if necessary (NIR usually grayscale).
2. Resize or central-crop to square (512×512 recommended).
3. Apply CLAHE (adaptive histogram equalization) to enhance furrows.
4. Detect iris/pupil center using Hough circles or segmentation centroid.
5. Save cropped images into `data/working/images/`.

## Quality Checks
- Implement `quality_check.py` to compute blur/SNR metrics.
- Filter images with low quality_score (< 0.7 recommended).

## Augmentation (safe)
- Small rotations (±10°)
- Brightness/contrast jitter (small)
- Gaussian noise (low sigma)
- Random patch cropping (nnU-Net handles internal patching)
- Avoid color augmentations (NIR)

## Polar unwrap
- Implement polar unwrapping using OpenCV `remap` for texture analysis.
- Save unwrapped images if using strip-based detectors.
