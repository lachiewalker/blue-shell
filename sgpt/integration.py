bash_integration = """
# BlueShell integration BASH v0.2
_blus_bash() {
if [[ -n "$READLINE_LINE" ]]; then
    READLINE_LINE=$(blus --shell <<< "$READLINE_LINE" --no-interaction)
    READLINE_POINT=${#READLINE_LINE}
fi
}
bind -x '"\\C-l": _blus_bash'
# BlueShell integration BASH v0.2
"""

zsh_integration = """
# BlueShell integration ZSH v0.2
_blus_zsh() {
if [[ -n "$BUFFER" ]]; then
    _blus_prev_cmd=$BUFFER
    BUFFER+="⌛"
    zle -I && zle redisplay
    BUFFER=$(blus --shell <<< "$_blus_prev_cmd" --no-interaction)
    zle end-of-line
fi
}
zle -N _blus_zsh
bindkey ^l _blus_zsh
# BlueShell integration ZSH v0.2
"""
