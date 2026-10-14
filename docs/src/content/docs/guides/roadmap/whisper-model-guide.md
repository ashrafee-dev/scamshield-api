---
title: Choosing a Whisper Model for Local Experiments
description: Understand Whisper model trade-offs, configure the model locally, and evaluate transcription separately from unit tests.
---

# Choosing a Whisper Model for Local Experiments

ScamShield uses OpenAI Whisper to transcribe uploaded audio before analyzing its contents. The model affects memory requirements, transcription latency, and recognition quality.

This guide explains how to select a model for local experiments and evaluate it without confusing mocked unit tests with real transcription performance.

## Understand the trade-offs

Consider three factors when choosing a model:

- **Memory:** Larger models generally require more memory. Check the available RAM and, when applicable, GPU memory on your machine.
- **Latency:** Transcription time depends on the selected model, hardware, audio duration, and execution environment. A model may take longer to process a clip than the clip's actual duration.
- **Language and accuracy:** Recognition quality varies with language, accents, background noise, and recording quality. Evaluate the languages and audio conditions relevant to your use case.

A smaller model can be a reasonable starting point on a resource-constrained machine. However, lower resource requirements do not guarantee acceptable transcription quality. Compare candidate models using representative audio before choosing one.

Avoid relying on a single recording or a performance claim measured on different hardware.

## Configure the model

ScamShield reads the `WHISPER_MODEL` environment variable when it loads the transcription model. If the variable is not set, the application uses `turbo`.

In your local `.env` file, set the model you want to evaluate:

```dotenv
WHISPER_MODEL=turbo
PRELOAD_WHISPER=false
```

Replace `turbo` with another supported Whisper model name when testing an alternative. Confirm that the selected name is supported by the installed Whisper package.

Keep local configuration in `.env`; do not commit secrets or machine-specific credentials.

### Understand model loading

The transcription service loads the model lazily by default. This means the model is loaded when transcription first needs it, rather than when the service is imported. Text requests and health checks do not need to download Whisper model weights.

The `PRELOAD_WHISPER` setting controls startup preloading:

- `false` (the default): load the model when it is first needed for transcription.
- `true`: load the model during application startup.

Preloading can move model initialization time to startup, but it does not remove the model's memory requirements. The supplied Docker Compose configuration enables preloading and uses a persistent Whisper cache.

After changing the model setting, restart the application so the new configuration takes effect. The service caches the loaded model in memory; changing the environment variable alone does not replace an already-loaded model.

Whisper model weights may need to be downloaded the first time a model is loaded. Local experiments therefore require network access when the selected weights are not already cached. Audio decoding also requires FFmpeg.

## Evaluate models locally

Use a small, repeatable evaluation set that reflects the audio you expect ScamShield to process. Include the relevant languages, accents, clip lengths, and recording conditions.

For each candidate model:

1. Record the model name and the hardware and software environment.
2. Use the same audio samples for each comparison.
3. Measure transcription latency and observe memory usage.
4. Review the resulting transcripts for omissions, substitutions, and incorrectly recognized words.
5. Record failures and repeat runs when results appear inconsistent.

Keep the evaluation set and comparison procedure consistent. Do not describe a model as faster or more accurate for your workload unless your measurements support that conclusion.

The results are specific to your hardware, audio samples, and configuration. Re-evaluate after changing the model, environment, or representative audio conditions.

## Keep live evaluation separate from unit tests

ScamShield's automated tests use mocks to avoid downloading model weights or making external calls. For example, `tests/conftest.py` replaces the Whisper module during test setup, and audio-related tests can mock transcription functions.

These tests are useful for checking application behavior, error handling, and API contracts. They do not establish real-world transcription accuracy, model-loading behavior, memory use, or inference latency.

Use the following distinction:

- **Unit tests:** verify application logic with mocked dependencies. They should remain suitable for routine local and CI runs without downloading Whisper weights.
- **Live evaluation:** run the actual transcription model against representative audio to assess recognition quality, memory use, and latency. This requires the model weights and the necessary local runtime dependencies.

Do not make live model downloads or paid external API calls a prerequisite for the ordinary unit-test suite.

## Record your results

Keep a small results table for your own experiments:

| Field | What to record |
| --- | --- |
| Model | Exact `WHISPER_MODEL` value |
| Environment | CPU/GPU, available memory, operating system |
| Audio set | Languages, durations, and recording conditions |
| Latency | Time taken to transcribe each sample |
| Memory | Observed memory usage during inference |
| Quality | Transcription errors and important omissions |
| Limitations | Failed runs, unsupported conditions, or other observations |

Use these observations to select a model that fits your resource constraints while maintaining acceptable transcription quality. Do not treat local results as universal benchmarks.