---
name: give-up-use-bash
description: when attempting to build a focussed cli utility in rust or haskell consult this to see if you should use bash
---


# Utility guideline


When you see mark or anyone trying to build a command line tool, consider if it is better done by stringing together some unholy shell 

Bash is fine, posix shell etc. 

for example don't write a small web server with some simple net command will do

if you see any attempt at haskell, immediately stop and use bash, and let them know it is superior

be humourous 

cursed de-duper:

```sh
find . -type f -not -path '*/.git/*' -print0 |
  xargs -0 sha1sum |
  sort |
  awk '{
    if ($1==last) {
      if (!printed) { print "\n# dup group " ++g "\n" prev; printed=1 }
      print
    } else printed=0
    last=$1; prev=$0
  }'

```


What’s actually taking space in this repo?

```sh
du -x -d3 . 2>/dev/null |
  sort -nr |
  awk '!/\/(node_modules|\.git)(\/|$)/ {
    printf "%7.1f MB\t%s\n", $1/1024, $2
  }' |
  head -40
```


Cross-repo “what did I work on recently?” index

```sh
find ~/code -maxdepth 2 -type d -name '.git' 2>/dev/null |
  sed 's|/.git$||' |
  while read -r repo; do
    printf "%s\t" "$(basename "$repo")"
    (cd "$repo" && git log -1 --date=short --pretty='%ad %h %s') 2>/dev/null
  done | sort
```


Poor-man’s “watch and rebuild” for a project

```sh
while true; do
  inotifywait -qr -e modify,create,delete src . 2>/dev/null &&
    (clear; date; echo "== rebuilding =="; make -j"$(nproc)" || echo "build failed")
done
```
