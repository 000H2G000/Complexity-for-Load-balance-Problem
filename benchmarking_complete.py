import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

# Importer les algorithmes (à partir du fichier précédent)
from load_balancing_algorithms import *

def load_benchmark_data(filename='load_balancing_benchmark.json'):
    """Charge les données de benchmark"""
    with open(filename, 'r') as f:
        return json.load(f)

def run_complete_benchmark(benchmark_suite, algorithms):
    """
    Exécute tous les algorithmes sur tous les benchmarks
    """
    all_results = []
    
    print("🚀 Démarrage du benchmarking complet...\n")
    
    for idx, instance in enumerate(benchmark_suite, 1):
        print(f"📊 Instance {idx}/{len(benchmark_suite)}: {instance['description']}")
        print("-" * 70)
        
        tasks = instance['tasks']
        n_servers = instance['n_servers']
        
        for algo_func, algo_name, params in algorithms:
            try:
                results, solution = evaluate_algorithm(
                    algo_func, tasks, n_servers, algo_name, **params
                )
                
                # Ajouter les informations de l'instance
                results['instance_id'] = instance['id']
                results['n_tasks'] = instance['n_tasks']
                results['n_servers'] = instance['n_servers']
                results['description'] = instance['description']
                
                all_results.append(results)
                
                print(f"  ✓ {algo_name:25s} | Makespan: {results['makespan']:6.0f} | "
                      f"Temps: {results['execution_time']:7.4f}s | Gap: {results['optimality_gap_%']:5.2f}%")
                
            except Exception as e:
                print(f"  ✗ {algo_name:25s} | ERREUR: {str(e)}")
        
        print()
    
    return pd.DataFrame(all_results)

def create_comparison_tables(df):
    """Crée des tableaux de comparaison"""
    
    print("\n" + "=" * 100)
    print("📋 TABLEAU RÉCAPITULATIF - MAKESPAN (Charge Maximale)")
    print("=" * 100)
    
    # Tableau makespan
    pivot_makespan = df.pivot(
        index='description', 
        columns='algorithm', 
        values='makespan'
    )
    print(pivot_makespan.to_string())
    
    print("\n" + "=" * 100)
    print("⏱️  TABLEAU RÉCAPITULATIF - TEMPS D'EXÉCUTION (secondes)")
    print("=" * 100)
    
    # Tableau temps
    pivot_time = df.pivot(
        index='description', 
        columns='algorithm', 
        values='execution_time'
    )
    print(pivot_time.to_string())
    
    print("\n" + "=" * 100)
    print("📊 TABLEAU RÉCAPITULATIF - GAP D'OPTIMALITÉ (%)")
    print("=" * 100)
    
    # Tableau gap
    pivot_gap = df.pivot(
        index='description', 
        columns='algorithm', 
        values='optimality_gap_%'
    )
    print(pivot_gap.to_string())
    
    return pivot_makespan, pivot_time, pivot_gap

def create_visualizations(df):
    """Crée des visualisations complètes"""
    
    algorithms = df['algorithm'].unique()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
    
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Makespan par instance
    ax1 = plt.subplot(2, 3, 1)
    for i, algo in enumerate(algorithms):
        algo_data = df[df['algorithm'] == algo]
        ax1.plot(range(len(algo_data)), algo_data['makespan'].values, 
                marker='o', label=algo, linewidth=2, color=colors[i])
    ax1.set_xlabel('Instance', fontsize=11)
    ax1.set_ylabel('Makespan (Charge Max)', fontsize=11)
    ax1.set_title('Comparaison du Makespan', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 2. Temps d'exécution
    ax2 = plt.subplot(2, 3, 2)
    for i, algo in enumerate(algorithms):
        algo_data = df[df['algorithm'] == algo]
        ax2.plot(range(len(algo_data)), algo_data['execution_time'].values, 
                marker='s', label=algo, linewidth=2, color=colors[i])
    ax2.set_xlabel('Instance', fontsize=11)
    ax2.set_ylabel('Temps (secondes)', fontsize=11)
    ax2.set_title('Temps d\'Exécution', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    # 3. Gap d'optimalité
    ax3 = plt.subplot(2, 3, 3)
    for i, algo in enumerate(algorithms):
        algo_data = df[df['algorithm'] == algo]
        ax3.plot(range(len(algo_data)), algo_data['optimality_gap_%'].values, 
                marker='^', label=algo, linewidth=2, color=colors[i])
    ax3.set_xlabel('Instance', fontsize=11)
    ax3.set_ylabel('Gap d\'Optimalité (%)', fontsize=11)
    ax3.set_title('Qualité de la Solution', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 4. Boxplot - Makespan
    ax4 = plt.subplot(2, 3, 4)
    df.boxplot(column='makespan', by='algorithm', ax=ax4)
    ax4.set_xlabel('Algorithme', fontsize=11)
    ax4.set_ylabel('Makespan', fontsize=11)
    ax4.set_title('Distribution du Makespan', fontsize=12, fontweight='bold')
    plt.sca(ax4)
    plt.xticks(rotation=15, ha='right', fontsize=9)
    
    # 5. Variance des charges
    ax5 = plt.subplot(2, 3, 5)
    for i, algo in enumerate(algorithms):
        algo_data = df[df['algorithm'] == algo]
        ax5.plot(range(len(algo_data)), algo_data['load_variance'].values, 
                marker='d', label=algo, linewidth=2, color=colors[i])
    ax5.set_xlabel('Instance', fontsize=11)
    ax5.set_ylabel('Variance des Charges', fontsize=11)
    ax5.set_title('Équilibrage de la Charge', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 6. Heatmap - Performance globale
    ax6 = plt.subplot(2, 3, 6)
    
    # Normaliser les métriques pour comparaison
    metrics_normalized = df.groupby('algorithm').agg({
        'makespan': 'mean',
        'execution_time': 'mean',
        'optimality_gap_%': 'mean',
        'load_variance': 'mean'
    })
    
    # Normaliser entre 0 et 1 (inverser pour makespan et temps car plus bas = mieux)
    for col in metrics_normalized.columns:
        metrics_normalized[col] = (metrics_normalized[col] - metrics_normalized[col].min()) / (metrics_normalized[col].max() - metrics_normalized[col].min())
    
    sns.heatmap(metrics_normalized.T, annot=True, fmt='.3f', cmap='RdYlGn_r', 
                cbar_kws={'label': 'Score Normalisé'}, ax=ax6, linewidths=0.5)
    ax6.set_xlabel('Algorithme', fontsize=11)
    ax6.set_ylabel('Métrique', fontsize=11)
    ax6.set_title('Performance Globale Normalisée', fontsize=12, fontweight='bold')
    plt.sca(ax6)
    plt.xticks(rotation=15, ha='right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('benchmarking_results.png', dpi=300, bbox_inches='tight')
    print("\n✅ Graphiques sauvegardés dans 'benchmarking_results.png'")
    plt.show()

def compute_statistics(df):
    """Calcule des statistiques détaillées"""
    
    print("\n" + "=" * 100)
    print("📈 STATISTIQUES DÉTAILLÉES PAR ALGORITHME")
    print("=" * 100)
    
    stats = df.groupby('algorithm').agg({
        'makespan': ['mean', 'std', 'min', 'max'],
        'execution_time': ['mean', 'std', 'min', 'max'],
        'optimality_gap_%': ['mean', 'std', 'min', 'max'],
        'load_variance': ['mean', 'std', 'min', 'max']
    }).round(4)
    
    print(stats.to_string())
    
    # Calculer les rangs moyens
    print("\n" + "=" * 100)
    print("🏆 CLASSEMENT MOYEN PAR CRITÈRE")
    print("=" * 100)
    
    rankings = pd.DataFrame()
    
    for metric in ['makespan', 'execution_time', 'optimality_gap_%', 'load_variance']:
        df[f'{metric}_rank'] = df.groupby('instance_id')[metric].rank(method='min')
    
    rank_summary = df.groupby('algorithm')[[
        'makespan_rank', 
        'execution_time_rank', 
        'optimality_gap_%_rank', 
        'load_variance_rank'
    ]].mean().round(2)
    
    rank_summary['rank_moyen_global'] = rank_summary.mean(axis=1).round(2)
    rank_summary = rank_summary.sort_values('rank_moyen_global')
    
    print(rank_summary.to_string())
    
    return stats, rank_summary

def analyze_complexity(df):
    """Analyse de la complexité par rapport à la taille"""
    
    print("\n" + "=" * 100)
    print("🔬 ANALYSE DE COMPLEXITÉ")
    print("=" * 100)
    
    # Grouper par taille
    complexity_analysis = df.groupby(['algorithm', 'n_tasks']).agg({
        'execution_time': 'mean',
        'makespan': 'mean'
    }).reset_index()
    
    print("\nTemps moyen par taille d'instance:")
    print(complexity_analysis.pivot(index='n_tasks', columns='algorithm', values='execution_time').to_string())
    
    # Graphique complexité
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    algorithms = df['algorithm'].unique()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
    
    for i, algo in enumerate(algorithms):
        algo_data = complexity_analysis[complexity_analysis['algorithm'] == algo]
        ax1.plot(algo_data['n_tasks'], algo_data['execution_time'], 
                marker='o', label=algo, linewidth=2, color=colors[i])
    
    ax1.set_xlabel('Nombre de Tâches', fontsize=12)
    ax1.set_ylabel('Temps d\'Exécution (s)', fontsize=12)
    ax1.set_title('Scalabilité des Algorithmes', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Efficacité (qualité / temps)
    for i, algo in enumerate(algorithms):
        algo_df = df[df['algorithm'] == algo]
        efficiency = (100 - algo_df['optimality_gap_%']) / (algo_df['execution_time'] + 0.0001)
        ax2.scatter(algo_df['n_tasks'], efficiency, 
                   label=algo, alpha=0.6, s=100, color=colors[i])
    
    ax2.set_xlabel('Nombre de Tâches', fontsize=12)
    ax2.set_ylabel('Efficacité (Qualité / Temps)', fontsize=12)
    ax2.set_title('Efficacité Computationnelle', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('complexity_analysis.png', dpi=300, bbox_inches='tight')
    print("\n✅ Graphiques de complexité sauvegardés dans 'complexity_analysis.png'")
    plt.show()

def generate_conclusions(rank_summary, df):
    """Génère des conclusions automatiques"""
    
    print("\n" + "=" * 100)
    print("📝 CONCLUSIONS ET RECOMMANDATIONS")
    print("=" * 100)
    
    best_overall = rank_summary.index[0]
    
    print(f"\n🏆 Meilleur algorithme global: {best_overall}")
    print(f"   Rang moyen: {rank_summary.iloc[0]['rank_moyen_global']}")
    
    # Meilleurs par critère
    best_makespan = df.groupby('algorithm')['makespan'].mean().idxmin()
    best_time = df.groupby('algorithm')['execution_time'].mean().idxmin()
    best_gap = df.groupby('algorithm')['optimality_gap_%'].mean().idxmin()
    
    print(f"\n🎯 Meilleur pour la QUALITÉ (makespan): {best_makespan}")
    print(f"   Makespan moyen: {df[df['algorithm'] == best_makespan]['makespan'].mean():.2f}")
    
    print(f"\n⚡ Plus RAPIDE: {best_time}")
    print(f"   Temps moyen: {df[df['algorithm'] == best_time]['execution_time'].mean():.4f}s")
    
    print(f"\n📊 Meilleur GAP d'optimalité: {best_gap}")
    print(f"   Gap moyen: {df[df['algorithm'] == best_gap]['optimality_gap_%'].mean():.2f}%")
    
    print("\n💡 RECOMMANDATIONS:")
    print("   • Pour petites instances (< 50 tâches): Privilégier l'Algorithme Glouton (rapidité)")
    print("   • Pour instances moyennes (50-200 tâches): Recherche Tabou (bon compromis)")
    print("   • Pour grandes instances (> 200 tâches): Dépend du temps disponible")
    print("   • Pour qualité optimale: Algorithme Génétique ou Recherche Tabou")
    print("   • Pour production temps réel: Algorithme Glouton")

def save_results_to_excel(df, pivot_makespan, pivot_time, pivot_gap, rank_summary):
    """Sauvegarde tous les résultats dans un fichier Excel"""
    
    with pd.ExcelWriter('benchmarking_results.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Résultats Complets', index=False)
        pivot_makespan.to_excel(writer, sheet_name='Makespan')
        pivot_time.to_excel(writer, sheet_name='Temps Exécution')
        pivot_gap.to_excel(writer, sheet_name='Gap Optimalité')
        rank_summary.to_excel(writer, sheet_name='Classements')
    
    print("\n✅ Résultats sauvegardés dans 'benchmarking_results.xlsx'")

# ============================================
# SCRIPT PRINCIPAL
# ============================================

if __name__ == "__main__":
    
    print("=" * 100)
    print(" " * 30 + "BENCHMARKING LOAD BALANCING")
    print("=" * 100)
    
    # Charger le benchmark
    try:
        benchmark_suite = load_benchmark_data()
        print(f"\n✅ {len(benchmark_suite)} instances chargées depuis 'load_balancing_benchmark.json'")
    except FileNotFoundError:
        print("\n⚠️  Fichier benchmark non trouvé. Génération d'un nouveau benchmark...")
        from generate_benchmark import generate_benchmark_suite
        benchmark_suite = generate_benchmark_suite()
    
    # Définir les algorithmes à tester
    algorithms = [
        (greedy_load_balancing, "Algorithme Glouton", {}),
        (tabu_search_load_balancing, "Recherche Tabou", 
         {'max_iterations': 100, 'tabu_tenure': 10}),
        (genetic_algorithm_load_balancing, "Algorithme Génétique", 
         {'population_size': 50, 'max_generations': 100, 'mutation_rate': 0.1})
    ]
    
    # Exécuter le benchmarking
    results_df = run_complete_benchmark(benchmark_suite, algorithms)
    
    # Créer les tableaux de comparaison
    pivot_makespan, pivot_time, pivot_gap = create_comparison_tables(results_df)
    
    # Calculer les statistiques
    stats, rank_summary = compute_statistics(results_df)
    
    # Créer les visualisations
    create_visualizations(results_df)
    
    # Analyser la complexité
    analyze_complexity(results_df)
    
    # Générer les conclusions
    generate_conclusions(rank_summary, results_df)
    
    # Sauvegarder dans Excel
    save_results_to_excel(results_df, pivot_makespan, pivot_time, pivot_gap, rank_summary)
    
    print("\n" + "=" * 100)
    print("✅ BENCHMARKING TERMINÉ AVEC SUCCÈS!")
    print("=" * 100)
    print("\n📁 Fichiers générés:")
    print("   • benchmarking_results.png - Visualisations comparatives")
    print("   • complexity_analysis.png - Analyse de scalabilité")
    print("   • benchmarking_results.xlsx - Résultats complets")
    print("\n" + "=" * 100)