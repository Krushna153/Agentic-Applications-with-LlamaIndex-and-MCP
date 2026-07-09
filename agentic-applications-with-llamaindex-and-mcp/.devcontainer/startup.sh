if [ -f requirements.txt ]; then
  pip install --user -r requirements.txt
  curl -fsSL https://claude.ai/install.sh | bash
fi
