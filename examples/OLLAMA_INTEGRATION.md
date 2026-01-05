# GhidraInsight - Ollama (Local AI) Integration Guide

> Run GhidraInsight with local AI models using Ollama - No API keys needed, full privacy, offline capable.

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: January 5, 2026

---

## 🦙 What is Ollama?

[Ollama](https://ollama.ai) is a simple, open-source tool that lets you run large language models locally on your machine. Unlike cloud-based APIs, local models run on your hardware - offering privacy, cost savings, and offline capability.

### Supported Models for GhidraInsight

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **Mistral** | 7B | ⚡ Fast | ⭐⭐⭐⭐ | General analysis (Recommended) |
| **Llama 2** | 7B-70B | ⚡ Fast to Slow | ⭐⭐⭐⭐ | Code analysis |
| **Neural Chat** | 7B | ⚡ Fast | ⭐⭐⭐ | Lightweight |
| **Orca** | 3B-13B | ⚡ Very Fast | ⭐⭐⭐ | Quick summaries |
| **CodeLLaMA** | 7B-34B | ⚡ Medium | ⭐⭐⭐⭐⭐ | Code-specific (Best for binaries) |

---

## 📋 System Requirements

### Minimum
- **RAM**: 8GB (for 7B models)
- **Disk**: 10GB free space
- **CPU**: Any modern processor
- **Internet**: Initial download only (optional after)

### Recommended
- **RAM**: 16GB+ (better performance)
- **GPU**: NVIDIA (CUDA) or Apple Silicon (Metal) for acceleration
- **Disk**: 50GB+ (multiple models)
- **CPU**: 6+ cores for concurrent analysis

---

## 🚀 Installation

### Step 1: Install Ollama

**macOS**:
```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Or use Homebrew
brew install ollama
```

**Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows (WSL2)**:
```bash
# In WSL2 terminal
curl -fsSL https://ollama.ai/install.sh | sh
```

**Verify Installation**:
```bash
ollama --version
# Should output: ollama version X.X.X
```

### Step 2: Download a Model

```bash
# Download Mistral (recommended, 4.1GB)
ollama pull mistral

# Or CodeLLaMA for binary analysis
ollama pull codellama

# Or Llama 2 for more power
ollama pull llama2
```

**Check Downloaded Models**:
```bash
ollama list
# Shows all available models
```

### Step 3: Start Ollama Server

```bash
# Start server (listens on http://localhost:11434)
ollama serve

# Or run in background
ollama serve &
```

**Verify Server**:
```bash
curl http://localhost:11434/api/tags
# Should return list of available models
```

---

## 🔗 Configure GhidraInsight

### Option 1: Interactive Configuration

```bash
# Setup guide (interactive)
ghidrainsight config setup --guided

# When prompted for LLM provider:
# Select: "Local (Ollama)"
# Model: "mistral" or "codellama"
# Endpoint: "http://localhost:11434"
```

### Option 2: Manual Configuration

**Create/Update `config.yaml`**:
```yaml
ai:
  providers:
    - name: ollama_local
      type: ollama
      enabled: true
      model: mistral              # or codellama, llama2
      endpoint: http://localhost:11434
      temperature: 0.7
      max_tokens: 2048
      
    - name: ollama_codellama
      type: ollama
      enabled: true
      model: codellama:34b
      endpoint: http://localhost:11434
      temperature: 0.5
      max_tokens: 4096

# Set default provider
default_provider: ollama_local
```

### Option 3: Environment Variables

```bash
# Set in shell
export GHIDRA_AI_PROVIDER=ollama
export GHIDRA_AI_MODEL=mistral
export GHIDRA_OLLAMA_ENDPOINT=http://localhost:11434

# Then start GhidraInsight
./scripts/startup.sh docker
```

**Add to `.env` file**:
```bash
GHIDRA_AI_PROVIDER=ollama
GHIDRA_AI_MODEL=mistral
GHIDRA_OLLAMA_ENDPOINT=http://localhost:11434
```

---

## 📖 Usage Examples

### Using Local AI in Web Dashboard

1. **Make sure Ollama is running**:
   ```bash
   # In another terminal
   ollama serve
   ```

2. **Open Dashboard**: http://localhost:3000

3. **Upload Binary**: Drag and drop your binary file

4. **Use AI Chat**: Type natural language questions
   ```
   "What crypto algorithms are used?"
   "Summarize main functions"
   "Find potential vulnerabilities"
   "Analyze data flow for user input"
   ```

### Using Local AI via Python SDK

```python
import asyncio
from ghidrainsight.client import GhidraInsightClient

async def analyze_with_local_ai():
    # Connect to GhidraInsight with Ollama backend
    client = GhidraInsightClient(
        "http://localhost:8000",
        ai_provider="ollama_local"  # Use local Ollama
    )
    
    # Analyze binary
    results = await client.analyze(
        file_path="/path/to/binary",
        features=["crypto", "vulnerabilities"],
        ai_powered=True  # Use local AI for analysis
    )
    
    # Results now include AI insights from local model
    print(f"AI Summary: {results.ai_summary}")
    print(f"Vulnerabilities: {results.vulnerabilities}")
    
    return results

# Run analysis
asyncio.run(analyze_with_local_ai())
```

### Using Local AI via CLI

```bash
# Analyze with local AI
ghidrainsight analyze \
    --file binary.elf \
    --ai-provider ollama \
    --ai-model mistral \
    --ai-summary \
    --output report.json

# Chat with binary
ghidrainsight chat \
    --file binary.elf \
    --ai-provider ollama \
    --prompt "What are the main vulnerabilities?"

# Batch analysis with local AI
ghidrainsight batch \
    --directory ./binaries \
    --ai-provider ollama \
    --output ./results
```

---

## 🎯 Model Selection Guide

### For Quick Analysis (Fastest)
```bash
ollama pull orca
# 3.3GB, very fast, good for summaries
```

### For General Binary Analysis (Recommended)
```bash
ollama pull mistral
# 4.1GB, balanced, excellent quality
```

### For Deep Code Analysis (Best)
```bash
ollama pull codellama:34b
# 20GB, slower, excellent code understanding
```

### For Production Deployments
```bash
ollama pull neural-chat
# 4.7GB, fast, efficient, good for servers
```

---

## ⚙️ Advanced Configuration

### GPU Acceleration

**NVIDIA GPUs (CUDA)**:
```bash
# Install CUDA (if not already)
# Then Ollama will auto-detect and use GPU

# Check if GPU is being used
ollama list  # Shows model sizes and usage
```

**Apple Silicon (Metal)**:
```bash
# Automatic - M1/M2/M3 Macs will use Metal automatically
# Check Activity Monitor to verify GPU usage
```

### Memory Management

**Reduce Memory Usage**:
```yaml
# In config.yaml
ai:
  providers:
    - name: ollama_local
      model: mistral
      # Reduce batch size for lower RAM usage
      batch_size: 256  # Default: 512
      # Limit context window
      max_tokens: 1024  # Default: 2048
```

### Custom Endpoints

```bash
# Run Ollama on different port
OLLAMA_HOST=0.0.0.0:11435 ollama serve

# Configure GhidraInsight to use custom port
ghidrainsight config set ollama.endpoint http://localhost:11435
```

### Model Optimization

```bash
# Run Ollama with custom settings
ollama serve \
  --addr 0.0.0.0:11434 \
  --num-threads 8 \
  --gpu-layers 20  # Number of GPU layers

# Or set environment variables
export OLLAMA_NUM_THREAD=8
export OLLAMA_GPU_LAYERS=20
ollama serve
```

---

## 🔒 Security & Privacy

### Local-Only Analysis
```bash
# All analysis happens locally, no data sent to cloud
ghidrainsight analyze --file binary.elf --ai-provider ollama

# Verify no internet connectivity required
curl -v http://localhost:8000/health
# Should work offline (assuming models are cached)
```

### Firewall Configuration

**Block External AI Services**:
```bash
# Only allow local connections
sudo ufw allow from 127.0.0.1 to any port 8000  # GhidraInsight API
sudo ufw allow from 127.0.0.1 to any port 11434 # Ollama
```

### Sensitive Data Handling

```yaml
# In config.yaml - Don't log sensitive data
logging:
  level: INFO
  include_prompts: false  # Don't log AI prompts
  include_results: false  # Don't log analysis results
  file: /secure/location/logs.txt
```

---

## 📊 Performance Comparison

### Analysis Time (Binary: 5MB)

| Model | RAM | Time | Quality |
|-------|-----|------|---------|
| Ollama Orca 3B | 6GB | 45s | ⭐⭐⭐ |
| **Ollama Mistral 7B** | **8GB** | **60s** | **⭐⭐⭐⭐** |
| Ollama Llama2 13B | 12GB | 90s | ⭐⭐⭐⭐ |
| Ollama CodeLLaMA 34B | 20GB | 120s | ⭐⭐⭐⭐⭐ |
| OpenAI GPT-4 API | ∞ | 5s | ⭐⭐⭐⭐⭐ |
| Claude API | ∞ | 10s | ⭐⭐⭐⭐⭐ |

**Best Balance**: Mistral (7B) - Fast enough for interactive use, good quality

---

## 🐛 Troubleshooting

### "Connection refused" Error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve &

# Wait 2 seconds for startup
sleep 2

# Try again
ghidrainsight analyze --file binary.elf --ai-provider ollama
```

### "Model not found" Error

```bash
# List available models
ollama list

# Download missing model
ollama pull mistral

# Verify download
ollama list
```

### High CPU Usage

```bash
# Reduce thread count
export OLLAMA_NUM_THREAD=4
ollama serve

# Or limit GPU layers
export OLLAMA_GPU_LAYERS=10
ollama serve
```

### Slow Analysis Speed

```bash
# Use smaller model (faster)
ollama pull neural-chat  # 4.7GB, very fast

# Or use GPU acceleration
# Install NVIDIA CUDA or use Apple Silicon
```

### "Out of Memory" Error

```bash
# Use smaller model
ollama pull orca:3b  # Only 3.3GB

# Or increase system swap
# macOS: System Preferences → Memory Tab
# Linux: sudo dd if=/dev/zero of=/swapfile bs=1G count=16

# Or reduce max_tokens in config
ghidrainsight config set ai.max_tokens 1024
```

---

## 🔄 Multi-Model Setup

### Run Multiple Models

```bash
# Terminal 1: Orca for fast analysis
OLLAMA_HOST=127.0.0.1:11434 ollama serve

# Terminal 2: CodeLLaMA for detailed analysis
OLLAMA_HOST=127.0.0.1:11435 ollama serve

# Terminal 3: Start GhidraInsight
export OLLAMA_ENDPOINTS="localhost:11434,localhost:11435"
./scripts/startup.sh docker
```

### Config for Multiple Models

```yaml
ai:
  providers:
    - name: ollama_fast
      model: orca:3b
      endpoint: http://localhost:11434
      use_for: quick_summaries
      
    - name: ollama_detailed
      model: codellama:34b
      endpoint: http://localhost:11435
      use_for: deep_analysis
      
    - name: ollama_balanced
      model: mistral
      endpoint: http://localhost:11434
      use_for: default

default_provider: ollama_balanced
```

---

## 📚 Additional Resources

### Official Ollama
- 🌐 [Ollama Website](https://ollama.ai)
- 📖 [Ollama Documentation](https://github.com/ollama/ollama)
- 🦙 [Model Library](https://ollama.ai/library)

### Model Information
- **Mistral**: https://mistral.ai/
- **Llama**: https://llama.meta.com/
- **CodeLLaMA**: https://about.fb.com/news/2023/08/code-llama-ai/

### Community & Support
- 💬 [Ollama Discussions](https://github.com/ollama/ollama/discussions)
- 🐛 [Ollama Issues](https://github.com/ollama/ollama/issues)
- 🔗 [GhidraInsight Discussions](https://github.com/ismailtsdln/GhidraInsight/discussions)

---

## 🎯 Best Practices

### 1. Start with Mistral
```bash
ollama pull mistral  # Good balance of speed and quality
```

### 2. Keep Server Running in Background
```bash
# macOS: Install LaunchAgent
# Linux: Use systemd service
# Windows: Use Task Scheduler
```

### 3. Monitor Resource Usage
```bash
# Check memory usage
top | grep ollama

# Monitor GPU
nvidia-smi  # For NVIDIA
metal stats  # For Apple Silicon
```

### 4. Cache Models Locally
```bash
# Models are cached in ~/.ollama/models/
# Keep a backup for offline use
```

### 5. Use Appropriate Model for Task
```bash
# Quick summaries → Orca
# Balanced analysis → Mistral  
# Code deep-dive → CodeLLaMA
# Production → Neural Chat
```

---

## 💡 Tips & Tricks

### Pre-load Model on Startup
```bash
# Add to your shell startup file
ollama pull mistral  # Pre-download
ollama serve &      # Start in background
```

### Compare Analyses with Multiple Models
```python
async def compare_models():
    models = ["mistral", "codellama", "llama2"]
    for model in models:
        results = await client.analyze(
            file_path="binary.elf",
            ai_model=model
        )
        print(f"\n{model}:\n{results.summary}")
```

### Create Analysis Benchmarks
```bash
# Test different models
for model in mistral llama2 codellama; do
    time ghidrainsight analyze --file binary.elf --ai-model $model
done
```

---

## 🚀 Next Steps

1. ✅ Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. ✅ Download Model: `ollama pull mistral`
3. ✅ Start Server: `ollama serve`
4. ✅ Configure GhidraInsight: `ghidrainsight config setup --guided`
5. ✅ Run Analysis: `ghidrainsight analyze --file binary.elf --ai-provider ollama`
6. ✅ Open Dashboard: http://localhost:3000

---

## 📝 Feedback

Have suggestions for Ollama integration? 
→ [GitHub Discussions](https://github.com/ismailtsdln/GhidraInsight/discussions)

---

**Privacy-Focused • Open Source • Fast • Free**

*Enjoy powerful local AI analysis without cloud dependencies!*

*Last Updated: January 5, 2026*
