#!/usr/bin/env bash
set -e

TARGET_GLOBAL="$HOME/.gemini/config/skills/prompt-cache-orchestrator"
SOURCE_SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/prompt-cache-orchestrator/SKILL.md"

echo "⚡ Installing Prompt Cache Orchestrator into Antigravity..."

if [ ! -f "$SOURCE_SKILL" ]; then
    echo "❌ Error: Skill source not found at: $SOURCE_SKILL"
    exit 1
fi

mkdir -p "$TARGET_GLOBAL"
cp "$SOURCE_SKILL" "$TARGET_GLOBAL/SKILL.md"

echo "✅ Successfully installed globally at:"
echo "   $TARGET_GLOBAL/SKILL.md"
echo ""
echo "Antigravity can now automatically use the 'prompt-cache-orchestrator' skill!"
