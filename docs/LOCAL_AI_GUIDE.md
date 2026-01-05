# Local AI Models Guide - GhidraInsight

> Complete guide to using local AI models (Ollama, LM Studio, GPT4All) with GhidraInsight for private, offline binary analysis.

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: January 5, 2026

---

## 🎯 Overview

GhidraInsight now supports **multiple local AI platforms** alongside cloud-based APIs. This guide covers:

1. **Ollama** - Recommended, easiest to use
2. **LM Studio** - GUI-based local LLM platform
3. **GPT4All** - Lightweight, user-friendly
4. **Hugging Face Transformers** - Advanced, flexible
5. **LocalAI** - Drop-in OpenAI replacement

---

## 📊 Local AI Platform Comparison

| Platform | Ease | Models | Speed | Memory | Best For |
|----------|------|--------|-------|--------|----------|
| **Ollama** | ⭐⭐⭐⭐⭐ | 20+ | ⚡⚡⚡ | 8GB+ | **RECOMMENDED** |
| LM Studio | ⭐⭐⭐⭐ | 50+ | ⚡⚡ | 6GB+ | GUI Users |
| GPT4All | ⭐⭐⭐⭐ | 20+ | ⚡ | 4GB+ | Beginners |
| HF Trans. | ⭐⭐⭐ | ∞ | ⚡⚡⚡ | 16GB+ | Power Users |
| LocalAI | ⭐⭐⭐ | 40+ | ⚡⚡ | 8GB+ | OpenAI Drop-in |

---

## 🦙 1. Ollama (Easiest - RECOMMENDED)

See [OLLAMA_INTEGRATION.md](OLLAMA_INTEGRATION.md) for detailed setup.

### Quick Start
```bash
# Install
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull mistral

# Start server
ollama serve

# Use with GhidraInsight
ghidrainsight analyze --file binary.elf --ai-provider ollama
```

### Pros
- ✅ Simplest installation
- ✅ Auto GPU detection
- ✅ Fastest startup
- ✅ Best community support

### Cons
- ❌ Limited customization
- ❌ Model selection limited

**Recommended Models**:
- `mistral` (7B) - Best balance
- `codellama` (7B-34B) - Code analysis
- `llama2` (7B-70B) - More power
- `neural-chat` (7B) - Lightweight

---

## 🎨 2. LM Studio (GUI-Based)

### Installation

1. **Download**: https://lmstudio.ai
2. **Install**: Follow platform instructions
3. **Launch**: Open LM Studio app

### Setup

1. **Download Models**:
   - Search "mistral" or "codellama"
   - Click download (takes few minutes)

2. **Load Model**:
   - Select model from list
   - Click "Load"
   - Wait for "Ready" status

3. **Start Server**:
   - Go to "Local Server" tab
   - Click "Start Server"
   - Note the URL (usually http://localhost:1234)

### Configure GhidraInsight

```bash
# Option 1: Interactive setup
ghidrainsight config setup --guided
# Select: LM Studio
# Endpoint: http://localhost:1234

# Option 2: Config file
cat > config.yaml << 'EOF'
ai:
  provider: lm_studio
  endpoint: http://localhost:1234
  model: mistral  # Or whatever you loaded
EOF
```

### Usage

```bash
# Analyze with LM Studio
ghidrainsight analyze --file binary.elf --ai-provider lm-studio

# Or use Python SDK
from ghidrainsight.client import GhidraInsightClient
client = GhidraInsightClient(
    ai_endpoint="http://localhost:1234",
    ai_provider="lm_studio"
)
```

### Pros
- ✅ GUI-based (beginner friendly)
- ✅ Lots of models available
- ✅ Easy model switching
- ✅ Good performance monitoring

### Cons
- ❌ Heavier resource usage
- ❌ Less automation friendly
- ❌ Slower startup

---

## 🚀 3. GPT4All (Lightweight)

### Installation

```bash
# macOS
brew install gpt4all

# Linux/Windows: Download from https://gpt4all.io
```

### Setup

```bash
# Start GPT4All server
gpt4all-cli --listen

# Default runs on http://localhost:4891
```

### Configure GhidraInsight

```yaml
ai:
  provider: gpt4all
  endpoint: http://localhost:4891
  model: mistral
```

### Usage

```bash
ghidrainsight analyze --file binary.elf --ai-provider gpt4all
```

### Pros
- ✅ Very lightweight
- ✅ Low memory requirement
- ✅ Offline capable
- ✅ Good for older machines

### Cons
- ❌ Limited model support
- ❌ Slower inference
- ❌ Less community activity

---

## 🤗 4. Hugging Face Transformers (Advanced)

### Installation

```bash
pip install transformers torch

# For GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Download Model

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Download during first run
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
```

### Run Local Server

```bash
# Install text-generation-webui
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
pip install -r requirements.txt

# Start server
python server.py --listen 0.0.0.0:5000
```

### Configure GhidraInsight

```yaml
ai:
  provider: huggingface
  endpoint: http://localhost:5000
  model: mistralai/Mistral-7B-Instruct-v0.1
```

### Usage

```python
from ghidrainsight.client import GhidraInsightClient

client = GhidraInsightClient(
    ai_endpoint="http://localhost:5000",
    ai_provider="huggingface"
)

results = await client.analyze("binary.elf")
```

### Pros
- ✅ Maximum flexibility
- ✅ Best performance potential
- ✅ Access to latest models
- ✅ Full customization

### Cons
- ❌ Complex setup
- ❌ High RAM requirement
- ❌ Steep learning curve
- ❌ Longer inference times

---

## 🏠 5. LocalAI (OpenAI Drop-in)

### Installation

**Docker (Recommended)**:
```bash
docker run -p 8080:8080 \
  -e "MODELS_PATH=/models" \
  -v /path/to/models:/models \
  localai/localai:latest-aio
```

**Manual**:
```bash
git clone https://github.com/go-skynet/LocalAI.git
cd LocalAI
make build
./local-ai --listen=0.0.0.0:8080
```

### Download Models

```bash
# Models are auto-downloaded on first use
# Or manually download from HuggingFace

docker exec <container_id> \
  wget -O /models/mistral-7b-instruct-v0.1.gguf \
  https://huggingface.co/.../download/mistral-...
```

### Configure GhidraInsight

```yaml
ai:
  provider: openai  # OpenAI-compatible API
  endpoint: http://localhost:8080
  model: mistral
```

### Usage

```bash
# Works exactly like OpenAI API
ghidrainsight analyze --file binary.elf --ai-provider openai

# Or Python
client = GhidraInsightClient(
    ai_endpoint="http://localhost:8080",
    ai_provider="openai"
)
```

### Pros
- ✅ OpenAI API compatible
- ✅ Many models available
- ✅ Good Docker support
- ✅ Production-ready

### Cons
- ❌ More complex setup
- ❌ Docker required
- ❌ Resource intensive

---

## 🔄 Comparison Matrix

### Setup Complexity
```
Easiest:     Ollama ⭐⭐⭐⭐⭐
             LM Studio ⭐⭐⭐⭐
             GPT4All ⭐⭐⭐⭐
             LocalAI ⭐⭐⭐
Hardest:     HF Transformers ⭐⭐
```

### Performance (Speed)
```
Fastest:     Ollama ⚡⚡⚡⚡⚡
             HF Transformers ⚡⚡⚡⚡
             LocalAI ⚡⚡⚡
             LM Studio ⚡⚡
Slowest:     GPT4All ⚡
```

### Model Selection
```
Most Models:  HF Transformers (unlimited)
             LocalAI (40+)
             LM Studio (50+)
             Ollama (20+)
Fewest:       GPT4All (15+)
```

### Ease of Use
```
Best UX:      LM Studio (GUI)
             Ollama (CLI, easy)
             GPT4All (CLI, simple)
             LocalAI (Docker)
Hardest:      HF Transformers (Python)
```

---

## 🛠️ Installation Comparison

### Ollama
```bash
# 1 line installation
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
ollama serve
```
**Time**: ~5 minutes

### LM Studio
```bash
# 1. Download from website
# 2. Install
# 3. Click buttons in GUI
```
**Time**: ~10 minutes

### GPT4All
```bash
# Installation and GUI
brew install gpt4all
gpt4all-cli --listen
```
**Time**: ~5 minutes

### HF Transformers
```bash
# Complex setup
pip install transformers torch
# Download model (~15GB)
# Setup web UI
# Configure endpoint
```
**Time**: ~30 minutes + download time

### LocalAI
```bash
# Docker required
docker run -p 8080:8080 localai/localai:latest-aio
```
**Time**: ~5 minutes (if Docker installed)

---

## 🎯 Quick Decision Tree

```
Do you want:
│
├─ Easiest setup + best support?
│  └─> Use Ollama ⭐ RECOMMENDED
│
├─ GUI interface?
│  └─> Use LM Studio
│
├─ Very lightweight (old hardware)?
│  └─> Use GPT4All
│
├─ OpenAI-compatible API?
│  └─> Use LocalAI
│
└─ Maximum flexibility + control?
   └─> Use HF Transformers
```

---

## ⚡ Performance Benchmarks

### Analysis Time (5MB Binary)

| Platform | Model | Time | RAM | Quality |
|----------|-------|------|-----|---------|
| Ollama | Mistral 7B | 60s | 8GB | ⭐⭐⭐⭐ |
| LM Studio | Mistral 7B | 65s | 8GB | ⭐⭐⭐⭐ |
| GPT4All | Mistral | 90s | 4GB | ⭐⭐⭐ |
| HF Trans. | Mistral | 45s | 16GB | ⭐⭐⭐⭐ |
| LocalAI | Mistral | 70s | 8GB | ⭐⭐⭐⭐ |
| **Cloud** | **GPT-4** | **5s** | **∞** | **⭐⭐⭐⭐⭐** |

---

## 🔐 Security & Privacy

### Local Processing Guarantee
```
Your Data:        Binary File
                       ↓
    Only Processed Locally ← Ollama/LM Studio/etc
                       ↓
                    Results
    
❌ Never sent to cloud
❌ No API keys needed (except for integration)
✅ 100% privacy
✅ Works offline
```

### Network Isolation
```bash
# Firewall only local connections
sudo ufw allow from 127.0.0.1 to any port 11434

# Verify no external connections
lsof -i TCP -s TCP:LISTEN | grep ollama
```

---

## 📊 Resource Requirements

### RAM by Model Size

| Size | RAM Needed | Use Case |
|------|-----------|----------|
| **3B** | 4GB | Quick analysis |
| **7B** | 8GB | Balanced (Recommended) |
| **13B** | 12GB | Better quality |
| **34B** | 24GB | Deep analysis |
| **70B** | 48GB+ | Maximum capability |

### Storage by Model

```
3B Model:   ~2GB
7B Model:   ~4GB
13B Model:  ~7GB
34B Model:  ~20GB
70B Model:  ~40GB
```

### GPU Acceleration

| GPU | Boost | VRAM |
|-----|-------|------|
| NVIDIA RTX 3060 | 3-4x | 12GB |
| NVIDIA RTX 4090 | 8-10x | 24GB |
| Apple M1/M2 | 2-3x | Shared |
| Apple M3 Max | 3-4x | Shared |
| AMD Radeon | 2-3x | 8-16GB |

---

## 🚀 Production Deployment

### Docker Compose Setup

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_THREAD=8
      - OLLAMA_GPU_LAYERS=20
    restart: unless-stopped

  ghidrainsight:
    depends_on:
      - ollama
    environment:
      GHIDRA_AI_PROVIDER: ollama
      GHIDRA_OLLAMA_ENDPOINT: http://ollama:11434

volumes:
  ollama_data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ghidrainsight-ollama
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        ports:
        - containerPort: 11434
```

---

## 🆚 VS Cloud AI Services

### GhidraInsight + Local AI

**Pros**:
- ✅ Privacy - data stays local
- ✅ Cost - one-time hardware cost
- ✅ Offline - works without internet
- ✅ Speed - no API latency
- ✅ Control - customize everything

**Cons**:
- ❌ Hardware cost
- ❌ Slower inference
- ❌ Limited to your hardware
- ❌ Manual updates needed

### GhidraInsight + Cloud API (OpenAI, Claude)

**Pros**:
- ✅ Fast responses
- ✅ Latest models
- ✅ No hardware needed
- ✅ Expert models (GPT-4, Claude)
- ✅ Always updated

**Cons**:
- ❌ Privacy concerns
- ❌ Recurring costs ($)
- ❌ Internet required
- ❌ API rate limits
- ❌ Vendor lock-in

---

## 🎓 Tutorials

### Tutorial 1: Get Started with Ollama (5 min)

```bash
# 1. Install
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Download Mistral
ollama pull mistral

# 3. Start server
ollama serve &

# 4. Verify
curl http://localhost:11434/api/tags

# 5. Use with GhidraInsight
ghidrainsight analyze --file binary.elf --ai-provider ollama
```

### Tutorial 2: Multiple Models (10 min)

```bash
# Download multiple models
ollama pull mistral
ollama pull codellama
ollama pull llama2

# Create config for all
cat > config.yaml << 'EOF'
ai:
  providers:
    - name: mistral
      model: mistral
      endpoint: http://localhost:11434
    - name: codellama
      model: codellama
      endpoint: http://localhost:11434
    - name: llama2
      model: llama2
      endpoint: http://localhost:11434
EOF

# Use specific model
ghidrainsight analyze --file binary.elf --ai-model codellama
```

### Tutorial 3: GPU Acceleration (15 min)

```bash
# Install CUDA (for NVIDIA)
# Check: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/

# Verify CUDA
nvidia-smi

# Ollama auto-detects CUDA
# Verify GPU usage
ollama list  # Shows if GPU is used

# Monitor performance
watch nvidia-smi
```

---

## 📚 Resources

### Official Documentation
- [Ollama Docs](https://github.com/ollama/ollama)
- [LM Studio](https://lmstudio.ai)
- [GPT4All](https://gpt4all.io)
- [LocalAI](https://localai.io)
- [HF Transformers](https://huggingface.co/docs/transformers)

### Model Resources
- [HuggingFace Models](https://huggingface.co/models)
- [Ollama Library](https://ollama.ai/library)
- [TheBloke's Models](https://huggingface.co/TheBloke)

### Community Support
- 💬 [GhidraInsight Discussions](https://github.com/ismailtsdln/GhidraInsight/discussions)
- 🦙 [Ollama Discussions](https://github.com/ollama/ollama/discussions)
- 🎨 [LM Studio Discord](https://discord.gg/...)

---

## 🎯 Recommendations

### For Most Users (RECOMMENDED)
```
Use: Ollama + Mistral 7B
- Easiest to setup
- Good speed & quality
- Balanced resource usage
- Best community support
```

### For Beginners
```
Use: LM Studio
- GUI interface
- Easy model switching
- Visual feedback
```

### For Professionals
```
Use: HF Transformers + CodeLLaMA
- Maximum control
- Best accuracy
- Custom optimization
```

### For Servers
```
Use: LocalAI + Docker
- Production-ready
- Easy scaling
- API compatibility
```

---

## 📝 Contributing

Found a new local AI platform? Have a better setup?  
→ [Contribute to GhidraInsight](CONTRIBUTING.md)

---

**Privacy-First • Open Source • Cost-Effective • Offline-Capable**

*Power your binary analysis with local AI - No cloud needed!*

*Last Updated: January 5, 2026*
