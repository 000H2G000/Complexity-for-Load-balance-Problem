import json
import os
import pandas as pd
from datetime import datetime

BENCH_JSON = 'load_balancing_benchmark.json'
OUT_HTML = 'benchmark_overview.html'


def load_benchmark(path=BENCH_JSON):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_dataframe(bench):
    rows = []
    for inst in bench:
        total = sum(inst['tasks'])
        lb = total / inst['n_servers']
        rows.append({
            'ID': inst.get('id', ''),
            'Description': inst.get('description', ''),
            'N_Tasks': inst['n_tasks'],
            'N_Servers': inst['n_servers'],
            'Total_Charge': total,
            'Lower_Bound': round(lb, 2)
        })
    df = pd.DataFrame(rows)
    return df


def html_escape(s: str) -> str:
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;'))


def make_html(df: pd.DataFrame):
    # Simple inline CSS for readability
    css = """
    body { font-family: Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
    h1 { margin-bottom: 4px; }
    h2 { margin-top: 28px; }
    .meta { color: #666; font-size: 0.95rem; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f5f5f5; text-align: left; }
    tr:nth-child(even) { background: #fafafa; }
    .img-wrap { display: grid; grid-template-columns: 1fr; gap: 12px; }
    .img-wrap img { max-width: 100%; border: 1px solid #e1e1e1; }
    .note { color: #555; font-size: 0.9rem; }
    """

    images = []
    for img in ['benchmark_visualization.png', 'benchmarking_results.png', 'complexity_analysis.png']:
        if os.path.exists(img):
            images.append(img)

    html = [
        '<!doctype html>',
        '<html lang="fr">',
        '<head>',
        '<meta charset="utf-8">',
        f'<title>Benchmark Overview</title>',
        f'<style>{css}</style>',
        '</head>',
        '<body>',
        '<h1>Benchmark Overview</h1>',
        f'<div class="meta">Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>',
        '<p class="note">Ce tableau synthétise ce qui est imprimé dans la console (Total charge et Borne inférieure optimale par instance). Les graphiques ci-dessous viennent des scripts existants.</p>',
        '<h2>Instances</h2>',
        df.to_html(index=False, justify='left'),
    ]

    if images:
        html.append('<h2>Graphiques générés</h2>')
        html.append('<div class="img-wrap">')
        for img in images:
            html.append(f'<div><div class="meta">{html_escape(img)}</div><img src="{html_escape(img)}" alt="{html_escape(img)}"/></div>')
        html.append('</div>')

    html.extend(['</body>', '</html>'])
    return '\n'.join(html)


def main():
    if not os.path.exists(BENCH_JSON):
        raise FileNotFoundError(f"{BENCH_JSON} introuvable. Exécutez generate_benchmark.py d'abord.")
    bench = load_benchmark(BENCH_JSON)
    df = build_dataframe(bench)
    html = make_html(df)
    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Tableau de synthèse généré dans '{OUT_HTML}' ({len(df)} lignes)")
    if os.path.exists('benchmark_visualization.png'):
        print("ℹ️  Les graphiques existants sont intégrés s'ils sont trouvés dans le dossier.")


if __name__ == '__main__':
    main()
