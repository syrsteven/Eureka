<p align="center">
  <img src="assets/eureka-readme-title.png" alt="Eureka human-in-the-loop digital medical research agent" width="760" />
</p>

# Eureka

Eureka is a human-in-the-loop LLM agent framework for digital medical research. It helps researchers turn clinical questions, multimodal datasets, and expert feedback into executable analysis workflows while keeping humans responsible for scientific direction, validation, and interpretation.

## Highlights

- Human-AI collaborative research workflow for digital medicine.
- Iterative loop of reasoning, planning, execution, reflection, and expert feedback.
- Support for file operations, web search, code execution, data analysis, modeling, and result summarization.
- Designed for traceable and supervised research rather than fully autonomous discovery.
- Evaluated on fixed-goal medical AI tasks and an open-goal nephropathy biomarker discovery study.

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://docs.docker.com/get-started/get-docker/)
- OpenAI-compatible API key, such as `OPENAI_API_KEY` or `DEEPSEEK_API_KEY`
- GPU tasks only: NVIDIA driver, Docker GPU support, and
  [NVIDIA Container Runtime](https://nvidia.github.io/nvidia-container-runtime/)

## Installation

```bash
git clone https://github.com/syrsteven/Eureka.git
cd Eureka
```

Configure environment variables:

```bash
cp .env.template .env
```

Then edit `.env` for your model provider, for example:

```env
OPENAI_API_KEY=your-openai-api-key
```

Install Python dependencies:

```bash
poetry install
```

For development and tests:

```bash
poetry install --with dev
```

## Docker

Docker is required for containerized tool execution and isolated workloads.

Pull the prebuilt Docker image for deep learning training:

```bash
docker pull syrsteven/autods:0.1.0
```

If you run GPU-based deep learning tasks, install NVIDIA Container Runtime and
verify Docker can access the GPU:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

If the command shows your GPU, Docker is ready for Eureka GPU workloads.

## Quick Start

Show help:

```bash
poetry run eureka --help
```

Start Eureka:

```bash
poetry run eureka
```

Windows users can also use:

```bat
eureka.bat --help
```

Linux/macOS users can also use:

```bash
./eureka.sh --help
```

## Project Structure

```text
eureka/      Core agent, commands, tools, memory, model providers, and app server
tests/       Unit and integration tests
assets/      README and project assets
scripts/     Helper scripts
data/        Local workspace placeholder
plugins/     Optional plugin workspace
```

## Disclaimer

Eureka is an experimental research system. Outputs should be reviewed by domain experts and must not be used as clinical decisions without appropriate validation and governance.
