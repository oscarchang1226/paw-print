# Only set this when we actually have a tty
if tty >/dev/null 2>&1; then
  export GPG_TTY="$(tty)"
fi

# Start agent quietly
gpgconf --launch gpg-agent >/dev/null 2>&1 || true