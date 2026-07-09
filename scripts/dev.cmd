@echo off
REM Wrapper so the preview/dev server has Node on PATH regardless of the
REM parent shell's (possibly stale) environment. Prepends the Node install dir
REM so nested `node`/`astro` invocations resolve, then runs the Astro dev server.
set "PATH=C:\Program Files\nodejs;%PATH%"
call "C:\Program Files\nodejs\npm.cmd" run dev -- --host
