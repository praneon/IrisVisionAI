# VLM Prompt Templates

## Simple prompt
You are an expert in structural iris analysis. Given the JSON summary and a small overlay image, generate a concise, non-diagnostic research-style description.

JSON:
{
 "image_id":"img_001",
 "features":[{"type":"lacuna","sector":3,"size":"large"}, ...],
 "counts": {"lacuna":2, "crypt":1}
}

Instruction:
"Describe structural observations and potential non-diagnostic interpretations. Avoid medical claims."

## Hybrid prompt (rule + VLM)
First present the deterministic rule-based summary, then ask the VLM to expand into coherent language with context and confidence scores.
