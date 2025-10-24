import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt

def generate_load_balancing_instance(n_tasks, n_servers, task_duration_range=(1, 100), seed=None):
    """
    Génère une instance du problème de Load Balancing
    
    Args:
        n_tasks: Nombre de tâches à répartir
        n_servers: Nombre de serveurs disponibles
        task_duration_range: Tuple (min, max) pour les durées des tâches
        seed: Graine aléatoire pour reproductibilité
    
    Returns:
        dict: Instance du problème avec tâches et serveurs
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Génération des durées de tâches
    tasks = np.random.randint(
        task_duration_range[0], 
        task_duration_range[1] + 1, 
        size=n_tasks
    )
    
    instance = {
        'n_tasks': n_tasks,
        'n_servers': n_servers,
        'tasks': tasks.tolist(),
        'task_duration_range': task_duration_range
    }
    
    return instance

def generate_benchmark_suite():
    """
    Génère un ensemble complet de benchmarks avec différentes tailles
    """
    benchmark_suite = []
    
    # Configurations de test : (n_tasks, n_servers, description)
    configurations = [
        # Petites instances
        (10, 2, "Petit - 10 tâches, 2 serveurs"),
        (20, 3, "Petit - 20 tâches, 3 serveurs"),
        (30, 4, "Petit - 30 tâches, 4 serveurs"),
        
        # Instances moyennes
        (50, 5, "Moyen - 50 tâches, 5 serveurs"),
        (100, 8, "Moyen - 100 tâches, 8 serveurs"),
        (150, 10, "Moyen - 150 tâches, 10 serveurs"),
        
        # Grandes instances
        (300, 15, "Grand - 300 tâches, 15 serveurs"),
        (500, 20, "Grand - 500 tâches, 20 serveurs"),
        (1000, 25, "Grand - 1000 tâches, 25 serveurs"),
    ]
    
    for i, (n_tasks, n_servers, description) in enumerate(configurations):
        instance = generate_load_balancing_instance(
            n_tasks=n_tasks,
            n_servers=n_servers,
            task_duration_range=(1, 100),
            seed=42 + i  # Pour reproductibilité
        )
        instance['id'] = f"instance_{i+1}"
        instance['description'] = description
        benchmark_suite.append(instance)
    
    return benchmark_suite

def save_benchmark_to_files(benchmark_suite, format='json'):
    """
    Sauvegarde les benchmarks dans des fichiers
    """
    if format == 'json':
        with open('load_balancing_benchmark.json', 'w') as f:
            json.dump(benchmark_suite, f, indent=2)
        print("✅ Benchmark sauvegardé dans 'load_balancing_benchmark.json'")
    
    elif format == 'csv':
        # Créer un DataFrame pour les statistiques
        stats = []
        for instance in benchmark_suite:
            stats.append({
                'ID': instance['id'],
                'Description': instance['description'],
                'N_Tasks': instance['n_tasks'],
                'N_Servers': instance['n_servers'],
                'Min_Duration': min(instance['tasks']),
                'Max_Duration': max(instance['tasks']),
                'Mean_Duration': np.mean(instance['tasks']),
                'Total_Load': sum(instance['tasks']),
                'Optimal_Lower_Bound': sum(instance['tasks']) / instance['n_servers']
            })
        
        df = pd.DataFrame(stats)
        df.to_csv('load_balancing_benchmark_stats.csv', index=False)
        print("✅ Statistiques sauvegardées dans 'load_balancing_benchmark_stats.csv'")

def visualize_benchmark(benchmark_suite):
    """
    Visualise les caractéristiques du benchmark
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Distribution des tailles d'instances
    n_tasks = [inst['n_tasks'] for inst in benchmark_suite]
    n_servers = [inst['n_servers'] for inst in benchmark_suite]
    
    axes[0, 0].bar(range(len(benchmark_suite)), n_tasks, alpha=0.7, label='Nombre de tâches')
    axes[0, 0].bar(range(len(benchmark_suite)), n_servers, alpha=0.7, label='Nombre de serveurs')
    axes[0, 0].set_xlabel('Instance')
    axes[0, 0].set_ylabel('Nombre')
    axes[0, 0].set_title('Tailles des Instances')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Charge totale par instance
    total_loads = [sum(inst['tasks']) for inst in benchmark_suite]
    axes[0, 1].plot(range(len(benchmark_suite)), total_loads, marker='o', linewidth=2)
    axes[0, 1].set_xlabel('Instance')
    axes[0, 1].set_ylabel('Charge Totale')
    axes[0, 1].set_title('Charge Totale par Instance')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Distribution des durées de tâches (première instance)
    first_instance = benchmark_suite[0]
    axes[1, 0].hist(first_instance['tasks'], bins=20, edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Durée de Tâche')
    axes[1, 0].set_ylabel('Fréquence')
    axes[1, 0].set_title(f"Distribution des Durées - {first_instance['description']}")
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Borne inférieure optimale
    lower_bounds = [sum(inst['tasks']) / inst['n_servers'] for inst in benchmark_suite]
    axes[1, 1].plot(range(len(benchmark_suite)), lower_bounds, marker='s', linewidth=2, color='green')
    axes[1, 1].set_xlabel('Instance')
    axes[1, 1].set_ylabel('Makespan Optimal (Borne Inf.)')
    axes[1, 1].set_title('Borne Inférieure Théorique')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benchmark_visualization.png', dpi=300, bbox_inches='tight')
    print("✅ Visualisation sauvegardée dans 'benchmark_visualization.png'")
    plt.show()

# Génération du benchmark complet
print("🔧 Génération du benchmark de Load Balancing...\n")
benchmark_suite = generate_benchmark_suite()

# Affichage des informations
print(f"📊 Nombre d'instances générées : {len(benchmark_suite)}\n")
for instance in benchmark_suite:
    print(f"  • {instance['description']}")
    print(f"    - Total charge: {sum(instance['tasks'])}")
    print(f"    - Borne inférieure optimale: {sum(instance['tasks']) / instance['n_servers']:.2f}")
    print()

# Sauvegarde
save_benchmark_to_files(benchmark_suite, format='json')
save_benchmark_to_files(benchmark_suite, format='csv')

# Visualisation
visualize_benchmark(benchmark_suite)

print("\n✅ Benchmark généré avec succès!")
print("📁 Fichiers créés:")
print("   - load_balancing_benchmark.json")
print("   - load_balancing_benchmark_stats.csv")
print("   - benchmark_visualization.png")