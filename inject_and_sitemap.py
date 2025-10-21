import re
import datetime
from pathlib import Path

# --- Font preload links ---
PRELOAD_LINKS = '''
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Syne&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Syne&display=swap" rel="stylesheet"></noscript>

<link rel="preload" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap" rel="stylesheet"></noscript>

<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100;0,400;0,700;1,400&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100;0,400;0,700;1,400&display=swap" rel="stylesheet"></noscript>

<link rel="preload" href="https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,100;0,300;0,400;0,500;1,400&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,100;0,300;0,400;0,500;1,400&display=swap" rel="stylesheet"></noscript>
'''

# --- Injection code for head ---
HEAD_INJECTION = '''
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GB8W0JWL0Y"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-GB8W0JWL0Y');
</script>

<!-- Start cookieyes banner -->
<script id="cookieyes" type="text/javascript" src="https://cdn-cookieyes.com/client_data/9a9a59c61254f1ad3643ddef/script.js"></script>
<!-- End cookieyes banner -->

<!-- Favicon -->
<link rel="icon" type="image/x-icon" href="aot-favicon.ico">
<link rel="apple-touch-icon" href="aot-webclip.png">
''' + PRELOAD_LINKS + '''

<!-- Google reCAPTCHA -->
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
'''

# --- Footer year updater ---
FOOTER_INJECTION = '''
<script>
  document.addEventListener("DOMContentLoaded", function() {
    var yearElem = document.getElementById("year");
    if(yearElem) {
      yearElem.textContent = new Date().getFullYear();
    }
  });
</script>
'''

# --- CAPTCHA widget (only for about page) ---
CAPTCHA_WIDGET = '''
<div class="g-recaptcha" data-sitekey="6Lf8u_ErAAAAANEAhBlg6JMX4wb4fMsOqIFxyrTi"></div>
'''

def inject_into_html(filepath: Path):
    content = filepath.read_text(encoding='utf-8')
    modified = False

    # Inject HEAD content
    if '</head>' in content:
        content = content.replace('</head>', HEAD_INJECTION + '\n</head>', 1)
        modified = True
    else:
        print(f"⚠️  No </head> found in {filepath.name}. Skipping head injection.")

    # Inject FOOTER content
    if '</body>' in content:
        content = content.replace('</body>', FOOTER_INJECTION + '\n</body>', 1)
        modified = True
    else:
        print(f"⚠️  No </body> found in {filepath.name}. Skipping footer injection.")

    # Inject CAPTCHA only into about.html
    if 'about' in filepath.name.lower():
        new_content, count = re.subn(r'(<form\b[^>]*>)', r'\1' + CAPTCHA_WIDGET, content, count=1)
        if count > 0:
            content = new_content
            modified = True
            print(f'🔒 reCAPTCHA injected into {filepath.name}')
        else:
            print(f"⚠️  No <form> tag found in {filepath.name} to inject CAPTCHA.")

    if modified:
        filepath.write_text(content, encoding='utf-8')
        print(f'✅ Modified: {filepath.name}')
    else:
        print(f'⏩ Skipped (no changes): {filepath.name}')

def generate_sitemap(domain: str, base_dir: Path, output: str = 'sitemap.xml'):
    html_urls = []
    for file in base_dir.iterdir():
        if file.is_file() and file.suffix.lower() == '.html':
            rel = file.relative_to(base_dir).as_posix()
            url = domain.rstrip('/') + '/' + rel.lstrip('/')
            html_urls.append(url)

    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for url in html_urls:
        lines += [
            '  <url>',
            f'    <loc>{url}</loc>',
            f'    <lastmod>{now}</lastmod>',
            '  </url>'
        ]
    lines.append('</urlset>')

    sitemap_path = base_dir / output
    sitemap_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'📄 Sitemap generated: {sitemap_path} ({len(html_urls)} pages)')

def main():
    try:
        base_dir = Path(__file__).resolve().parent
    except NameError:
        base_dir = Path.cwd()

    print("📁 Working directory:", base_dir)

    # Set to True if you want to recurse into subfolders
    RECURSIVE = False

    html_files = base_dir.rglob('*.html') if RECURSIVE else base_dir.glob('*.html')

    for filepath in html_files:
        inject_into_html(filepath)

    generate_sitemap('https://damianbvoylan.com', base_dir)

if __name__ == '__main__':
    main()
