{\rtf1\ansi\ansicpg1252\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}}
{\*\generator Riched20 10.0.22621}\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang9 install:\par
\tab poetry install\par
\par
dev:\par
poetry run flask --app page_analyzer:app run\par
\par
PORT ?= 8000\par
start:\par
\tab poetry run gunicorn -w 5 -b 0.0.0.0:$(POST) page_analyzer:app\par
\par
}
 