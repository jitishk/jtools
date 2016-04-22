
set nocompatible
set history=50		" keep 50 lines of command line history
set ruler		    " show the cursor position all the time
set showcmd		    " display incomplete commands
set incsearch		" do incremental searching
set tabstop=4
set sw=4
set number
set expandtab

set statusline=
set statusline +=%1*\ %n\ %*            "buffer number
set statusline +=%5*%{&ff}%*            "file format
set statusline +=%3*%y%*                "file type
set statusline +=%4*\ %<%F%*            "full path
set statusline +=%2*%m%*                "modified flag
set statusline +=%1*%=%5l%*             "current line
set statusline +=%2*/%L%*               "total lines
set statusline +=%1*%4v\ %*             "virtual column number
set statusline +=%2*0x%04B\ %*          "character under cursor




" Disableing syntax on as it overrides syntax with vim defaults
" syntax on

" Enables syntax. Along with filetype should pick syntax by file
syntax enable

"Depending on filetype i.e. ext, the corresponding <ext>.vim is used
filetype plugin on
filetype indent on

highlight Comment ctermfg=lightblue

"Disabling smart indent. It interferes with '=' to autoindent
"set smartindent
"
" Enable copy-paste-yank in visual mode
set virtualedit=all

" In xterm lxapps, this is required for mouse-selecting
" For local/the mouse should work quite well, thus enable it.
set mouse=a

" Toggle paste for Insert (to avoid auto indent)
set pastetoggle=<F2>

set noswapfile
set nobackup
set nowritebackup   " Donot make a backup before overwriting a file.

set splitright      " Open vsplit to right of current buffer
set splitbelow      " Open split to bottom of current buffer

"Shows matching bracket
set showmatch
"Amount of time to show matching bracket
set matchtime=3


"""""""""""""""""""""""""""""" KEY MAPS """"""""""""""""""""""""""""""
" Opens a shell in vim
map _vs :ConqueTermVSplit bash<CR>
map _hs :ConqueTermSplit bash<CR>

" FILE FORMATTING 
" Remove Prompt :%s/<C-v><C-[>>//g
" Remove Bell   :%s/<C-v><C-g>//g
map _l :%s/<C-v><C-[>\[K\\|<C-v><C-[>\[?1l\\|---(more)---\\|\[Press space to continue, 'q' to quit.\]\\|<C-v><C-[>\[7m\\|<C-v><C-[>\[m\\|<C-v><C-[>\[?1h\\|<C-v><C-[>=\\|<C-v><C-[>>\\|<C-v><C-g>\\|<C-v><C-[>\[27m\\|<C-v><C-m>//g<CR>

" Handle ^H characters in script-generated files
"
map _m :%s/[^<C-v><C-h>]<C-v><C-h>//g<CR>
"Fold lines between []"
map _f zfa[

" Remove whitespace
map _w :%s/\s\+$//<CR>
 
" Function example
map _t :call ScriptCleanup()<CR>
function! ScriptCleanup()
    echo $VIMRUNTIME
endfunction

" allow backspacing over everything in insert mode
set backspace=indent,eol,start
map!  


set hlsearch
if has("autocmd")
  filetype plugin indent on
else
  set autoindent
endif " has("autocmd")



"autocmd vimenter * NERDTree
"autocmd vimenter * if !argc() | NERDTree NERDTreeTabsOpen | endif

"let g:nerdtree_tabs_open_on_new_tab=1
" let g:nerdtree_tabs_open_on_console_startup=1
"let g:nerdtree_tabs_open_on_gui_startup=1
"let g:nerdtree_tabs_synchronize_view=1
"let g:nerdtree_tabs_focus_on_files=1
"let g:nerdtree_tabs_startup_cd=1
"let g:NERDTreeDirArrows=0
 


" filetype plugin on
" set ofu=syntaxcomplete#Complete

" Convenient command to see the difference between the current buffer and the
" file it was loaded from, thus the changes you made.
" command DiffOrig vert new | set bt=nofile | r # | 0d_ | diffthis
" 	 	\ | wincmd p | diffthis
" autocmd FileType python set omnifunc=pythoncomplete#Complete
" autocmd FileType c set omnifunc=ccomplete#Complete

" map <F5>f I/**<CR>@func<CR>@brief<CR>@param<CR>@return<CR>/ <Esc>


