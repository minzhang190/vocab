#!/usr/bin/env python

html_head = '''
<!doctype html>
<html>
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

		<title>reveal.js</title>

		<link rel="stylesheet" href="css/reveal.css">
		<link rel="stylesheet" href="css/theme/black.css">

		<link rel="stylesheet" href="css/vocab.css">

		<!-- Theme used for syntax highlighting of code -->
		<link rel="stylesheet" href="lib/css/zenburn.css">

		<!-- Printing and PDF exports -->
		<script>
			var link = document.createElement( 'link' );
			link.rel = 'stylesheet';
			link.type = 'text/css';
			link.href = window.location.search.match( /print-pdf/gi ) ? 'css/print/pdf.css' : 'css/print/paper.css';
			document.getElementsByTagName( 'head' )[0].appendChild( link );
		</script>
	</head>
	<body>
		<div class="reveal">
			<div class="slides">
'''

html_tail = '''
			</div>
		</div>

		<script src="lib/js/head.min.js"></script>
		<script src="js/reveal.js"></script>

		<script>
			// More info https://github.com/hakimel/reveal.js#configuration
			Reveal.initialize({
				history: true,

                                transition: 'none',

				// More info https://github.com/hakimel/reveal.js#dependencies
				dependencies: [
					{ src: 'plugin/markdown/marked.js' },
					{ src: 'plugin/markdown/markdown.js' },
					{ src: 'plugin/notes/notes.js', async: true },
					{ src: 'plugin/highlight/highlight.js', async: true, callback: function() { hljs.initHighlightingOnLoad(); } }
				]
			});
		</script>
	</body>
</html>
'''

import codecs
from pypinyin import pinyin

attribs = {
    'background_color': '',
    'text_color': '',
}

data = {}

text_pieces = [html_head]

inside = {
    'text': False,
    'table': False,
}

def fmt(fmtstr, locals_):
    fmtdict = attribs.copy()
    fmtdict.update(locals_)
    fmtdict['data_str'] = ' '.join(('%s="%s"' % x) for x in data.iteritems())
    text_pieces.append(fmtstr % fmtdict)

def sect(text, table, locals_):
    if text:
        if not inside['text']:
            inside['text'] = True
            fmt('''
                                                <div class=vocab-text style="color:%(text_color)s">
            ''', locals_)
        if table:
            if not inside['table']:
                inside['table'] = True
                fmt('''
                                                    <table class=vocab-text-table>
                ''', locals_)
        else:
            if inside['table']:
                inside['table'] = False
                fmt('''
                                                    </table>
                ''', locals_)
    else:
        if inside['table']:
            inside['table'] = False
            fmt('''
                                                </table>
            ''', locals_)
        if inside['text']:
            inside['text'] = False
            fmt('''
                                                </div>
            ''', locals_)

with codecs.open('input.txt', 'r', 'utf-8') as f:
    for row in f:
        row = row.strip()
        if '|' in row:
            last_str = ''
            class_ = ''
            data = {}
            fmt('''
				<section data-background-color="%(background_color)s">
					<div class=vocab-card>
            ''', locals())
            for piece in row.split('|'):
                if '=' not in piece:
                    continue
                cmd, text = piece.split('=', 1)
                if cmd == 'captain':
                    sect(True, False, locals())
                    fmt('''
                                                                <h2 class="vocab-text-captain %(class_)s" %(data_str)s>%(text)s</h2>
                    ''', locals())
                    last_str = text
                    class_ = ''
                    data = {}
                elif cmd == 'phrase':
                    sect(True, True, locals())
                    fmt('''
                                                                <tr class="%(class_)s" %(data_str)s>
                    ''', locals())
                    for ch in text:
                        fmt('''
                                                                    <td><h2 class=vocab-text-phrase>%(ch)s</h2>
                        ''', locals())
                    last_str = text
                    class_ = ''
                    data = {}
                elif cmd == 'string':
                    last_str = text
                elif cmd == 'class':
                    class_ = text
                elif cmd.startswith('data-'):
                    data[cmd] = text
                elif cmd == 'pinyin':
                    if text == '':
                        pyarr = [x[0] for x in pinyin(last_str)]
                    else:
                        pyarr = text.split()
                    sect(True, True, locals())
                    fmt('''
                                                                <tr class="%(class_)s" %(data_str)s>
                    ''', locals())
                    for ch in pyarr:
                        fmt('''
                                                                    <td><h2 class=vocab-text-pinyin>%(ch)s</h2>
                        ''', locals())
                    class_ = ''
                    data = {}
                elif cmd == 'image':
                    sect(False, False, locals())
                    fmt('''
                                                            <div class="vocab-image %(class_)s" %(data_str)s><img data-src="img/%(text)s"></div>
                    ''', locals())
                    class_ = ''
                    data = {}
            sect(False, False, locals())
            fmt('''
					</div>
				</section>
            ''', locals())
        elif '=' in row:
            attrib, value = row.split('=', 1)
            if attrib in attribs:
                attribs[attrib] = value

text_pieces.append(html_tail)

print '\n'.join(text_pieces).encode('utf-8')
