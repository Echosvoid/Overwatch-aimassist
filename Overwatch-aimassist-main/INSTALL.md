# Installation Guide

This guide will help you set up the Overwatch Aim Assist project on your system.

## Prerequisites

- Windows 10/11
- Python 3.8 or higher
- NVIDIA GPU (recommended)
- Overwatch installed

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Echosvoid/Overwatch-aimassist.git
cd Overwatch-aimassist
```

### 2. Set Up Python Environment

#### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure GPU Support (Optional but Recommended)

1. Install NVIDIA CUDA Toolkit
2. Install cuDNN
3. Set up environment variables:
   ```bash
   set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.0
   set PATH=%CUDA_PATH%\bin;%PATH%
   ```

### 5. Verify Installation

Run the test suite:
```bash
python -m pytest tests/
```

## Common Installation Issues

### 1. OpenCV Installation Fails

If you encounter issues installing OpenCV:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### 2. CUDA Support Issues

If CUDA support is not working:
1. Verify CUDA installation:
   ```bash
   nvcc --version
   ```
2. Check GPU compatibility:
   ```bash
   nvidia-smi
   ```

### 3. Python Version Issues

If you get Python version errors:
1. Check your Python version:
   ```bash
   python --version
   ```
2. Install the correct Python version if needed

## Post-Installation

1. Copy `config.json.example` to `config.json`
2. Adjust settings in `config.json`
3. Create your first profile:
   ```bash
   python src/utils/profile_manager.py create "My Profile"
   ```

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 3. Configure IDE

Recommended VS Code extensions:
- Python
- Pylance
- Python Test Explorer
- Python Docstring Generator

## Troubleshooting

If you encounter any issues during installation:

1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Search existing [GitHub Issues](https://github.com/Echosvoid/Overwatch-aimassist/issues)
3. Create a new issue if needed

## Support

For additional help:
- Join our [Discord Server](https://discord.gg/overwatch-aimassist)
- Check the [Documentation](docs/README.md)
- Contact the maintainers 