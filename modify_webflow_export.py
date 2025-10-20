import os
import re
import datetime

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

<link rel="preload" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet"></noscript>
'''

# --- Injection code ---
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
<script id="cookieyes" type="text/javascript" src="https://cdn-cookieyes.com/client_data/0186c326d2cb1a69ba616170/script.js"></script>
<!-- End cookieyes banner -->

<!-- Favicon -->
<link rel="icon" type="image/x-icon" href="db-favicon.ico">
<link rel="apple-touch-icon" href="db-webclip.png">
''' + PRELOAD_LINKS + '''
'''

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

# --- Sitemap generation ---
def generate_sitemap(domain, output='sitemap.xml'):
    html_urls = []
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name.endswith('.html'):
                rel_path = os.path.join(root, name).replace('\\', '/').lstrip('./')
                url_path = '/' + rel_path
                full_url = domain + url_path
                html_urls.append(full_url)

    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for url in html_urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{url}</loc>')
        lines.append(f'    <lastmod>{now}</lastmod>')
        lines.append('  </url>')

    lines.append('</urlset>')

    with open(output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'Sitemap generated with {len(html_urls)} URLs → {output}')

# --- Injecting the necessary code into HTML files ---
def inject_code_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject head code
    if '</head>' in content:
        content = content.replace('</head>', HEAD_INJECTION + '\n</head>')
    else:
        print(f'Warning: No </head> tag found in {filepath}, skipping head injection.')

    # Inject footer code
    if '</body>' in content:
        content = content.replace('</body>', FOOTER_INJECTION + '\n</body>')
    else:
        print(f'Warning: No </body> tag found in {filepath}, skipping footer injection.')

    # Remove Webflow badge(s)
    new_content = re.sub(
        r'<[^>]*class="[^"]*w-webflow-badge[^"]*"[^>]*>.*?</[^>]+>',
        '',
        content,
        flags=re.DOTALL
    )

    if new_content != content:
        content = new_content
        print(f'Removed Webflow badge from {filepath}')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Injected code in {filepath}')

# --- Main function ---
def main():
    print("Starting injection and cleanup...")

    # Loop through all HTML files and inject necessary code
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                inject_code_in_file(filepath)

    print("Injection and cleanup complete.\n")

    # Update the domain to reflect the new domain (damianboylan.com)
    domain = 'https://damianboylan.com'  # Corrected domain
    generate_sitemap(domain)

if __name__ == '__main__':
    main()