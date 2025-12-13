# Training Recipes

## nnU-Net (Segmentation)
- Convert COCO → nnU-Net dataset structure using `convert_coco_to_nnunet.py`.
- Example commands (nnU-Net CLI depends on installation):
  ```
  nnUNet_plan_and_preprocess -t TASK_ID --verify_dataset_integrity
  nnUNet_train 2d nnUNetTrainerV2 TaskXXX_FOLD0 --epochs 400 --batch_size 4
  ```
- Logging: W&B or TensorBoard.
- Hyperparameters: AdamW, lr=1e-3 (nnU-Net auto-configures), epochs=200-400, batch size based on GPU.

## YOLOv8 (Detection)
- Prepare dataset in YOLO format and `yolo_dataset.yaml`.
- Example command:
  ```
  yolo task=detect mode=train model=yolov8n.pt data=annotations/yolo_dataset.yaml imgsz=640 epochs=100 batch=16
  ```
- Monitor AP@0.5 and AP_small. Use -n for GTX1650.

## VLM
- Start with prompt engineering; provide JSON + small overlay image.
- Fine-tuning optional; require significant compute and dataset for reliable tuning.
