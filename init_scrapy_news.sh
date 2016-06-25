#!/usr/bin/env bash


#export TERM_PROGRAM=Apple_Terminal
#export SHELL=/bin/zsh
#export TERM=xterm-256color
#export TMPDIR=/var/folders/3p/7b_wv8x57bjg08f8mcrhtydh0000gn/T/
#export Apple_PubSub_Socket_Render=/private/tmp/com.apple.launchd.KLvPAeRQ6I/Render
#export TERM_PROGRAM_VERSION=361
#export TERM_SESSION_ID=9DCE90CF-0E20-43DA-824D-12A3A1E1D65A
#export USER=DQ
#export SSH_AUTH_SOCK=/private/tmp/com.apple.launchd.Y2kCfvriyt/Listeners
#export __CF_USER_TEXT_ENCODING=0x1F5:0x19:0x34
#export PATH=/usr/local/Cellar/pyenv-virtualenv/20160202/shims:/usr/local/Cellar/pyenv/20160303/libexec:/usr/local/var/pyenv/shims:/usr/local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH=/usr/local/bin
#export PWD=/Users/DQ/Desktop/Python/CHOOSE_STOCK/project
export LANG=zh_CN.UTF-8
#export XPC_FLAGS=0x0
#export XPC_SERVICE_NAME=0
#export SHLVL=1
#export HOME=/Users/DQ
#export LOGNAME=DQ
#export OLDPWD=/Users/DQ/Desktop/Python/CHOOSE_STOCK
#export ZSH=/Users/DQ/.oh-my-zsh
#export PAGER=less
#export LESS=-R
#export LC_CTYPE=zh_CN.UTF-8
#export LSCOLORS=Gxfxcxdxbxegedabagacad
#export VIRTUAL_ENV_DISABLE_PROMPT=1
#export PYENV_ROOT=/usr/local/var/pyenv
#export PYENV_SHELL=zsh
#export PYENV_VIRTUALENV_INIT=1



#export PWD=$HOME/Desktop/Python/CHOOSE_STOCK/project/s_c_stock
cd $HOME/Desktop/Python/CHOOSE_STOCK/project/s_c_stock
env
scrapy crawl choose_stock_news
#ls
#scrapy list
#echo '呱呱'
#pwd
#ls