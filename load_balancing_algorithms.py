import numpy as np
import time
import tracemalloc
from copy import deepcopy
import random

class LoadBalancingSolution:
    """Représente une solution du problème de Load Balancing"""
    def __init__(self, n_servers, tasks):
        self.n_servers = n_servers
        self.tasks = tasks
        self.assignment = [[] for _ in range(n_servers)]  # Tâches assignées à chaque serveur
        self.server_loads = [0] * n_servers
    
    def assign_task(self, task_id, server_id):
        """Assigne une tâche à un serveur"""
        task_duration = self.tasks[task_id]
        self.assignment[server_id].append(task_id)
        self.server_loads[server_id] += task_duration
    
    def get_makespan(self):
        """Retourne le makespan (charge maximale)"""
        return max(self.server_loads)
    
    def get_load_variance(self):
        """Retourne la variance des charges"""
        return np.var(self.server_loads)
    
    def copy(self):
        """Crée une copie de la solution"""
        new_sol = LoadBalancingSolution(self.n_servers, self.tasks)
        new_sol.assignment = deepcopy(self.assignment)
        new_sol.server_loads = self.server_loads.copy()
        return new_sol


# ============================================
# 1. ALGORITHME GLOUTON (Greedy)
# ============================================

def greedy_load_balancing(tasks, n_servers):
    """
    Algorithme glouton : LPT (Longest Processing Time)
    Assigne chaque tâche au serveur le moins chargé
    """
    solution = LoadBalancingSolution(n_servers, tasks)
    
    # Trier les tâches par durée décroissante (LPT)
    sorted_tasks = sorted(enumerate(tasks), key=lambda x: x[1], reverse=True)
    
    for task_id, task_duration in sorted_tasks:
        # Trouver le serveur le moins chargé
        min_server = np.argmin(solution.server_loads)
        solution.assign_task(task_id, min_server)
    
    return solution


# ============================================
# 2. RECHERCHE TABOU
# ============================================

def tabu_search_load_balancing(tasks, n_servers, max_iterations=100, tabu_tenure=10):
    """
    Recherche Tabou pour Load Balancing
    Mouvement : transférer une tâche d'un serveur à un autre
    """
    n_tasks = len(tasks)
    
    # Solution initiale (greedy)
    current_solution = greedy_load_balancing(tasks, n_servers)
    best_solution = current_solution.copy()
    
    # Liste tabou : stocke les mouvements interdits
    tabu_list = []
    
    for iteration in range(max_iterations):
        best_neighbor = None
        best_neighbor_makespan = float('inf')
        best_move = None
        
        # Explorer le voisinage
        for server_from in range(n_servers):
            if not current_solution.assignment[server_from]:
                continue
                
            for task_id in current_solution.assignment[server_from]:
                for server_to in range(n_servers):
                    if server_from == server_to:
                        continue
                    
                    move = (task_id, server_from, server_to)
                    
                    # Créer une solution voisine
                    neighbor = current_solution.copy()
                    neighbor.assignment[server_from].remove(task_id)
                    neighbor.server_loads[server_from] -= tasks[task_id]
                    neighbor.assignment[server_to].append(task_id)
                    neighbor.server_loads[server_to] += tasks[task_id]
                    
                    neighbor_makespan = neighbor.get_makespan()
                    
                    # Critère d'aspiration : accepter si meilleur que le meilleur global
                    is_tabu = move in tabu_list
                    aspiration = neighbor_makespan < best_solution.get_makespan()
                    
                    if (not is_tabu or aspiration) and neighbor_makespan < best_neighbor_makespan:
                        best_neighbor = neighbor
                        best_neighbor_makespan = neighbor_makespan
                        best_move = move
        
        if best_neighbor is None:
            break
        
        # Mettre à jour la solution courante
        current_solution = best_neighbor
        
        # Mettre à jour la meilleure solution
        if current_solution.get_makespan() < best_solution.get_makespan():
            best_solution = current_solution.copy()
        
        # Gérer la liste tabou
        if best_move:
            tabu_list.append(best_move)
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)
    
    return best_solution


# ============================================
# 3. ALGORITHME GÉNÉTIQUE
# ============================================

def genetic_algorithm_load_balancing(tasks, n_servers, population_size=50, 
                                     max_generations=100, mutation_rate=0.1):
    """
    Algorithme Génétique pour Load Balancing
    Chromosome : liste d'assignations [server_id pour chaque tâche]
    """
    n_tasks = len(tasks)
    
    def create_random_solution():
        """Crée un chromosome aléatoire"""
        return [random.randint(0, n_servers - 1) for _ in range(n_tasks)]
    
    def chromosome_to_solution(chromosome):
        """Convertit un chromosome en solution"""
        solution = LoadBalancingSolution(n_servers, tasks)
        for task_id, server_id in enumerate(chromosome):
            solution.assign_task(task_id, server_id)
        return solution
    
    def fitness(chromosome):
        """Fonction de fitness : inverse du makespan (à maximiser)"""
        solution = chromosome_to_solution(chromosome)
        return -solution.get_makespan()  # Négatif car on minimise makespan
    
    def selection(population, fitnesses):
        """Sélection par tournoi"""
        tournament_size = 3
        selected = []
        for _ in range(2):
            tournament = random.sample(list(zip(population, fitnesses)), tournament_size)
            winner = max(tournament, key=lambda x: x[1])
            selected.append(winner[0])
        return selected
    
    def crossover(parent1, parent2):
        """Croisement uniforme"""
        child1 = []
        child2 = []
        for i in range(n_tasks):
            if random.random() < 0.5:
                child1.append(parent1[i])
                child2.append(parent2[i])
            else:
                child1.append(parent2[i])
                child2.append(parent1[i])
        return child1, child2
    
    def mutate(chromosome):
        """Mutation : change l'assignation d'une tâche aléatoire"""
        mutated = chromosome.copy()
        for i in range(n_tasks):
            if random.random() < mutation_rate:
                mutated[i] = random.randint(0, n_servers - 1)
        return mutated
    
    # Initialisation de la population
    population = [create_random_solution() for _ in range(population_size)]
    
    # Inclure une solution greedy dans la population initiale
    greedy_sol = greedy_load_balancing(tasks, n_servers)
    greedy_chromosome = []
    for server_id, task_list in enumerate(greedy_sol.assignment):
        for task_id in task_list:
            greedy_chromosome.append((task_id, server_id))
    greedy_chromosome.sort()
    population[0] = [server_id for _, server_id in greedy_chromosome]
    
    best_chromosome = None
    best_fitness = float('-inf')
    
    # Évolution
    for generation in range(max_generations):
        # Évaluation
        fitnesses = [fitness(chrom) for chrom in population]
        
        # Mise à jour du meilleur
        gen_best_idx = np.argmax(fitnesses)
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness = fitnesses[gen_best_idx]
            best_chromosome = population[gen_best_idx].copy()
        
        # Nouvelle génération
        new_population = []
        
        # Élitisme : garder le meilleur
        new_population.append(best_chromosome)
        
        while len(new_population) < population_size:
            # Sélection
            parent1, parent2 = selection(population, fitnesses)
            
            # Croisement
            child1, child2 = crossover(parent1, parent2)
            
            # Mutation
            child1 = mutate(child1)
            child2 = mutate(child2)
            
            new_population.extend([child1, child2])
        
        population = new_population[:population_size]
    
    return chromosome_to_solution(best_chromosome)


# ============================================
# FONCTION D'ÉVALUATION AVEC MÉTRIQUES
# ============================================

def evaluate_algorithm(algorithm_func, tasks, n_servers, algorithm_name, **kwargs):
    """
    Évalue un algorithme et retourne les métriques
    """
    # Mesure du temps
    start_time = time.time()
    
    # Mesure de la mémoire
    tracemalloc.start()
    
    # Exécution de l'algorithme
    solution = algorithm_func(tasks, n_servers, **kwargs)
    
    # Fin des mesures
    execution_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Calcul des métriques
    makespan = solution.get_makespan()
    load_variance = solution.get_load_variance()
    optimal_lower_bound = sum(tasks) / n_servers
    optimality_gap = ((makespan - optimal_lower_bound) / optimal_lower_bound) * 100
    
    results = {
        'algorithm': algorithm_name,
        'makespan': makespan,
        'load_variance': round(load_variance, 2),
        'execution_time': round(execution_time, 4),
        'memory_peak_mb': round(peak / 1024 / 1024, 4),
        'optimal_lower_bound': round(optimal_lower_bound, 2),
        'optimality_gap_%': round(optimality_gap, 2),
        'server_loads': solution.server_loads
    }
    
    return results, solution


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    # Exemple simple
    tasks = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    n_servers = 3
    
    print("=" * 60)
    print("BENCHMARKING - LOAD BALANCING")
    print("=" * 60)
    print(f"\n📊 Problème : {len(tasks)} tâches, {n_servers} serveurs")
    print(f"Tâches : {tasks}")
    print(f"Charge totale : {sum(tasks)}")
    print(f"Borne inférieure optimale : {sum(tasks) / n_servers:.2f}\n")
    
    # Test des algorithmes
    algorithms = [
        (greedy_load_balancing, "Algorithme Glouton (LPT)", {}),
        (tabu_search_load_balancing, "Recherche Tabou", {'max_iterations': 100, 'tabu_tenure': 10}),
        (genetic_algorithm_load_balancing, "Algorithme Génétique", {'population_size': 50, 'max_generations': 100})
    ]
    
    for algo_func, algo_name, params in algorithms:
        print(f"\n🔍 {algo_name}")
        print("-" * 60)
        results, solution = evaluate_algorithm(algo_func, tasks, n_servers, algo_name, **params)
        
        print(f"  Makespan (charge max)    : {results['makespan']}")
        print(f"  Variance des charges     : {results['load_variance']}")
        print(f"  Temps d'exécution        : {results['execution_time']} secondes")
        print(f"  Mémoire pic              : {results['memory_peak_mb']} MB")
        print(f"  Gap d'optimalité         : {results['optimality_gap_%']}%")
        print(f"  Charges par serveur      : {results['server_loads']}")
    
    print("\n" + "=" * 60)