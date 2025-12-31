#!/usr/bin/env bash
#
# 项目环境一键设置脚本（macOS / Linux 兼容）
# 用法：
#   cd /Volumes/DJH/wy/ym/wykf
#   chmod +x scripts/setup_project.sh
#   ./scripts/setup_project.sh [--run]
# 若传入 --run 则在安装完成后会启动 `python main.py`

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Project root: $ROOT_DIR"

# 1) 如果存在 pyenv，尝试使用本地或创建推荐的 virtualenv
if command -v pyenv >/dev/null 2>&1; then
  echo "pyenv detected."
  if [ -f .python-version ]; then
    echo ".python-version found: $(cat .python-version)"
  else
    # prefer a named virtualenv, fallback to system 3.8.18 if available
    if pyenv versions --bare | grep -q '^property-manager-3.8$'; then
      echo "Using existing pyenv virtualenv: property-manager-3.8"
      pyenv local property-manager-3.8
    elif pyenv versions --bare | grep -q '^3.8.18$'; then
      echo "Setting local python to 3.8.18"
      pyenv local 3.8.18
    else
      echo "pyenv does not contain property-manager-3.8 nor 3.8.18."
      echo "If you want pyenv-managed venv, run:"
      echo "  pyenv virtualenv 3.8.18 property-manager-3.8"
      echo "  pyenv local property-manager-3.8"
    fi
  fi
  # initialize pyenv in this shell (safe if not present)
  eval "$(pyenv init -)"
fi

# 2) Create or activate .venv
if [ -d ".venv" ]; then
  echo "Activating existing .venv..."
  # shellcheck source=/dev/null
  source .venv/bin/activate
else
  echo "Creating .venv using current 'python' in PATH..."
  if ! command -v python >/dev/null 2>&1; then
    echo "Error: python not found in PATH. Ensure pyenv local is set or install Python."
    exit 1
  fi
  python -m venv .venv
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

echo "Python: $(python -V)"
echo "PIP: $(pip -V)"

# 3) Upgrade pip and install dependencies
python -m pip install --upgrade pip setuptools wheel
if [ -f requirements-win7.txt ]; then
  pip install -r requirements-win7.txt
else
  pip install -r requirements.txt
fi

# 4) Backup database (if exists) and run migrations
if [ -f property.db ]; then
  ts=$(date +%Y%m%d%H%M%S)
  cp property.db "property.db.bak.${ts}"
  echo "Backed up property.db -> property.db.bak.${ts}"
fi

echo "Running database migration..."
python migrate_db.py

# 5) Quick import test of modules
echo "Verifying project imports..."
python - <<'PY'
try:
    import models, services, ui
    print("Import check OK")
except Exception as e:
    print("Import check FAILED:", e)
    raise
PY

echo "Setup complete."

if [ "${1:-}" = "--run" ]; then
  echo "Starting application: python main.py"
  python main.py
fi


