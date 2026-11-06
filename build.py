"""Embed history.json into the template -> index.html (one self-contained file)."""
import datetime as dt
tpl = open('template_portfolio.html', encoding='utf-8').read()
blob = open('history.json', encoding='utf-8').read()
html = tpl.replace('/*__HISTORY__*/', 'const HISTORY = ' + blob.replace('</', r'<\/') + ';')
html = html.replace('__BUILT__', dt.datetime.now().strftime('%d %b %Y, %H:%M'))
open('index.html', 'w', encoding='utf-8').write(html)
print('index.html', round(len(html) / 1048576, 2), 'MB')
