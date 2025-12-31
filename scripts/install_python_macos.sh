#!/usr/bin/env bash
#
# 安装并配置 Python 3.8 开发环境（macOS）
# 说明：
#  - 本脚本使用 Homebrew 安装依赖，然后使用 pyenv 安装 Python 3.8.x（示例 3.8.18）。
#  - 运行前请确保你有管理员权限以安装 Homebrew / brew 包。
#  使用方法：
#    chmod +x scripts/install_python_macos.sh
#    ./scripts/install_python_macos.sh [3.8.18]
#  可选参数：指定 Python 3.8 的次版本（例如 3.8.18）。默认使用 3.8.18。

set -euo pipefail

PYVER="${1:-3.8.18}"

echo "开始在 macOS 上安装 Python ${PYVER} 开发环境（pyenv）..."

# 1) 安装 Homebrew（如已安装会跳过）
if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew 未检测到，正在安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew 已安装，更新 Homebrew..."
    brew update
fi

echo "安装构建 Python 所需的依赖（openssl@1.1 readline sqlite3 xz zlib pyenv）..."
brew install pyenv openssl@1.1 readline sqlite3 xz zlib || true

# 2) shell 配置建议（输出到终端，用户需手动将下面内容加入 ~/.zshrc 或 ~/.bash_profile）
PYENV_ROOT="$HOME/.pyenv"
BREW_OPENSSL_PREFIX="$(brew --prefix openssl@1.1 2>/dev/null || echo "")"
BREW_READLINE_PREFIX="$(brew --prefix readline 2>/dev/null || echo "")"
BREW_ZLIB_PREFIX="$(brew --prefix zlib 2>/dev/null || echo "")"

echo
echo "请将下面内容追加到你的 shell 配置文件（例如 ~/.zshrc 或 ~/.bash_profile）："
echo "------------------------------------------------------------"
echo "export PYENV_ROOT=\"$PYENV_ROOT\""
echo "export PATH=\"\$PYENV_ROOT/bin:\$PATH\""
echo "eval \"\$(pyenv init -)\""
if [ -n "$BREW_OPENSSL_PREFIX" ]; then
    echo "export LDFLAGS=\"-L$BREW_OPENSSL_PREFIX/lib -L$BREW_READLINE_PREFIX/lib -L$BREW_ZLIB_PREFIX/lib\""
    echo "export CPPFLAGS=\"-I$BREW_OPENSSL_PREFIX/include -I$BREW_READLINE_PREFIX/include -I$BREW_ZLIB_PREFIX/include\""
    echo "export PKG_CONFIG_PATH=\"$BREW_OPENSSL_PREFIX/lib/pkgconfig:$BREW_READLINE_PREFIX/lib/pkgconfig:$BREW_ZLIB_PREFIX/lib/pkgconfig\""
fi
echo "------------------------------------------------------------"
echo
echo "建议现在运行："
echo "  source ~/.zshrc   # 或者 source ~/.bash_profile"
echo
read -p "按回车键继续（确保已把上面内容加入你的 shell 配置并执行 source）..." _ || true

# 3) 安装指定 Python 版本
echo "开始使用 pyenv 安装 Python ${PYVER}（可能需要几分钟）..."
# 确保 pyenv 在 PATH
export PYENV_ROOT="$PYENV_ROOT"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv install --skip-existing "${PYVER}"
echo "Python ${PYVER} 已安装（若提示失败，请检查前面输出的错误信息并安装 Xcode Command Line Tools：xcode-select --install）"

# 4) 创建虚拟环境（pyenv-virtualenv 可选）
VENV_NAME="property-manager-${PYVER}"
if pyenv virtualenv --version >/dev/null 2>&1; then
    echo "创建 pyenv virtualenv：${VENV_NAME}"
    pyenv virtualenv --force "${PYVER}" "${VENV_NAME}" || true
    echo "在项目目录设置本地 Python 版本（将在 .python-version 写入）"
    echo "请在项目根目录运行： pyenv local ${VENV_NAME}"
else
    echo "pyenv-virtualenv 未安装或不可用，建议使用 venv："
    echo "  pyenv shell ${PYVER}"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
fi

echo
echo "安装完成后，请在项目根目录执行下面命令完成项目依赖安装："
echo "  cd /Volumes/DJH/wy/ym/wykf"
echo "  pyenv local ${VENV_NAME}   # 或者 source .venv/bin/activate"
echo "  python -m pip install --upgrade pip setuptools wheel"
echo "  pip install -r requirements.txt"
echo "  python migrate_db.py   # 运行迁移脚本（请先备份 property.db）"
echo "  python main.py         # 启动程序进行验证"

echo
echo "脚本执行完毕。"


