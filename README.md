---
title: mini-leaderboard
emoji: 🤖
colorFrom: purple
colorTo: purple
sdk: docker
pinned: false
app_port: 8909
---

# mini-leaderboard

[![Release](https://img.shields.io/github/v/release/wh1isper/mini-leaderboard)](https://img.shields.io/github/v/release/wh1isper/mini-leaderboard)
[![Build status](https://img.shields.io/github/actions/workflow/status/wh1isper/mini-leaderboard/main.yml?branch=main)](https://github.com/wh1isper/mini-leaderboard/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/wh1isper/mini-leaderboard/branch/main/graph/badge.svg)](https://codecov.io/gh/wh1isper/mini-leaderboard)
[![Commit activity](https://img.shields.io/github/commit-activity/m/wh1isper/mini-leaderboard)](https://img.shields.io/github/commit-activity/m/wh1isper/mini-leaderboard)
[![License](https://img.shields.io/github/license/wh1isper/mini-leaderboard)](https://img.shields.io/github/license/wh1isper/mini-leaderboard)

simple learderboard and messageboard with many projects

Try it on: https://wh1isper-mini-leaderboard.hf.space/

- demo leaderboard: https://th4wiw3hfz.app.youware.com/
- demo messageboard: https://tc61kg62zc.app.youware.com/

## How to prompt:

- Tell AI using API in https://wh1isper-mini-leaderboard.hf.space/openapi.json, If AI cannot access url, copy the content
- Use a `project_id` you like, e.g. `example-project`, this will allow you to get a leaderboard and messageboard for a specific project.

## Deploy your own

1. Fork the `mini-leaderboard` repo on GitHub or [Huggingface Space](https://huggingface.co/spaces/Wh1isper/mini-leaderboard/tree/main)
1. Push to your huggingface space
1. Set `DB_URL` in `Settings` of your huggingface space, e.g. `<username>:<password>.@<host>:<port>/<database>`

I'm using [supabase](https://supabase.com/) for the example service, but you can use any database you like.
