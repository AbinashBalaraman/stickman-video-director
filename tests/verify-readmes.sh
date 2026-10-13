#!/usr/bin/env bash
set -euo pipefail

readme_root=$(git rev-parse --show-toplevel)
default_readmes=(
  README.md
  README.en.md
  README.zh-CN.md
  README.ja.md
  README.ko.md
  README.pt-BR.md
)
demo_assets=(
  assets/readme/light-theme-demo.gif
  assets/readme/light-theme-demo.mp4
  assets/readme/dark-theme-demo.gif
  assets/readme/dark-theme-demo.mp4
  assets/readme/style-2a-demo.gif
  assets/readme/style-2a-demo.mp4
  assets/readme/style-2b-demo.gif
  assets/readme/style-2b-demo.mp4
  assets/readme/style-3-demo.gif
  assets/readme/style-3-demo.mp4
  assets/readme/style-3-community-fire.gif
  assets/readme/style-3-community-fire.mp4
)
section_markers=(
  '<!-- readme:hero -->'
  '<!-- readme:demos -->'
  '<!-- readme:advantages -->'
  '<!-- readme:platforms -->'
  '<!-- readme:workflow -->'
  '<!-- readme:output -->'
  '<!-- readme:install -->'
  '<!-- readme:reliability -->'
  '<!-- readme:contribute -->'
)
shared_tokens=(
  'README.md'
  'README.zh-CN.md'
  'README.ja.md'
  'README.ko.md'
  'README.pt-BR.md'
  'assets/readme/light-theme-demo.gif'
  'assets/readme/light-theme-demo.mp4'
  'assets/readme/dark-theme-demo.gif'
  'assets/readme/dark-theme-demo.mp4'
  'assets/readme/style-2a-demo.gif'
  'assets/readme/style-2a-demo.mp4'
  'assets/readme/style-2b-demo.gif'
  'assets/readme/style-2b-demo.mp4'
  'assets/readme/style-3-demo.gif'
  'assets/readme/style-3-demo.mp4'
  'assets/readme/style-3-community-fire.gif'
  'assets/readme/style-3-community-fire.mp4'
  'https://x.com/monixin888'
  'WorkBuddy'
  'YouTube Shorts'
  'TikTok'
  'Instagram Reels'
  'Gemini Omni Flash'
  '16:9'
  '9:16'
  '$directing-stickman-videos'
  'git clone https://github.com/kaomei/stickman-video-director.git'
  'cp -R skills/directing-stickman-videos'
  'MIT'
)

if (( $# > 0 )); then
  readmes=("$@")
else
  readmes=("${default_readmes[@]}")
fi

for asset in "${demo_assets[@]}"; do
  [[ -f "$readme_root/$asset" ]] || {
    printf 'missing demo asset: %s\n' "$asset" >&2
    exit 1
  }
done

for readme in "${readmes[@]}"; do
  readme_path="$readme_root/$readme"
  [[ -f "$readme_path" ]] || {
    printf 'missing README: %s\n' "$readme" >&2
    exit 1
  }

  for marker in "${section_markers[@]}"; do
    rg -Fq "$marker" "$readme_path" || {
      printf '%s missing section marker: %s\n' "$readme" "$marker" >&2
      exit 1
    }
  done

  for token in "${shared_tokens[@]}"; do
    rg -Fq "$token" "$readme_path" || {
      printf '%s missing shared token: %s\n' "$readme" "$token" >&2
      exit 1
    }
  done

  # Each style must keep two clickable examples in the same table row.
  for pair in 'light-theme-demo dark-theme-demo' 'style-2a-demo style-2b-demo' 'style-3-demo style-3-community-fire'; do
    read -r first_demo second_demo <<< "$pair"
    rg -q "href=\"assets/readme/${first_demo}\.mp4\".*[|].*href=\"assets/readme/${second_demo}\.mp4\"" "$readme_path" || {
      printf '%s missing paired examples: %s\n' "$readme" "$pair" >&2
      exit 1
    }
  done

  forbidden_identity='eva''2050|240669''650|/Users/''eva'
  forbidden_claims='guaranteed ''viral|guaranteed ''views'
  if rg -n "${forbidden_identity}|${forbidden_claims}" "$readme_path"; then
    printf '%s contains forbidden identity or unsupported claim\n' "$readme" >&2
    exit 1
  fi
done

printf 'README contract passed for %s file(s).\n' "${#readmes[@]}"
