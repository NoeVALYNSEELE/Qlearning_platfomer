import math
import numpy as np
import random
import pygame

# Paramètres de base
pygame.init()
LARGEUR = 800
HAUTEUR = 600
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Platformer Q-learning")

# Paramètres du personnage
LARGEUR_PERSO = 50
HAUTEUR_PERSO = 50
vitesse_perso = 5
vitesse_saut = 18
gravite = 1

# Couleurs
C1 = (135, 206, 235)
C2 = (25, 25, 112)
VERT_FONCE = (34, 139, 34)
VERT_CLAIR = (50, 205, 50)
BLEU = (25, 25, 200)
COULEUR_PERSONNAGE = (255, 69, 0)

# Plateformes
platformes = [
    pygame.Rect(0, HAUTEUR - 10, LARGEUR, 10),
    pygame.Rect(220, 450, 170, 10),
    pygame.Rect(450, 350, 250, 10),
    pygame.Rect(300, 220, 150, 10),
    pygame.Rect(550, 100, 50, 10)
]

# Objectif
objectif = pygame.Rect(570, 75, 20, 20)
objectif_atteint = False

# Danger
danger = [pygame.Rect(200, 570, 2000, 20),
          pygame.Rect(1, 570, 90, 20)]

# Objectifs intermédiaires
objectifs_intermediaires = [
    pygame.Rect(250, 430, 15, 15),
    pygame.Rect(550, 330, 15, 14),
]

# Q-learning paramètres
actions = [(0, 0), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1)]
gamma = 0.9
alpha = 0.1
epsilon = 0.1
states = (LARGEUR // 10, HAUTEUR // 10)
Q_table = np.zeros((states[0], states[1], len(actions)))

# Statistiques d'entraînement
victoire = 0
temps_victoires = []
FPS_60 = 60
FPS_50000 = 50000
FPS = FPS_60

# Fonction de suivi
def afficher_statistiques(temps_partie, state):
    if len(temps_victoires) > 0:
        moyenne_temps = sum(temps_victoires) / len(temps_victoires)
    else:
        moyenne_temps = 0

    valeur_Q_moyenne = np.mean(Q_table[state[0], state[1]])
    print(f"Victoires : {victoire} | Pourcentage Victoire : {(victoire/(victoire+mort_compteur))*100}% | Temps : {temps_partie} frames | TQ-table moy : {valeur_Q_moyenne:.2f}")

def afficher_q_table(state):
    print(f"\nQ-table pour l'état {state} :")
    for i, action in enumerate(actions):
        print(f"{action}: {Q_table[state][i]:.3f}")

# Fonction d'apprentissage Q-learning
def choisir_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, len(actions) - 1)
    
    # Récupérer la ligne de la Q-table correspondant à l'état
    q_values = Q_table[state[0], state[1]]
    
    # Trouver la valeur maximale
    max_q = np.max(q_values)
    
    # Trouver toutes les actions ayant cette valeur maximale
    best_actions = np.where(q_values == max_q)[0]
    
    # Choisir aléatoirement parmi elles
    return random.choice(best_actions)    

def mettre_a_jour_Q(state, action, reward, next_state):
    next_state = (min(states[0] - 1, max(0, next_state[0])),
                  min(states[1] - 1, max(0, next_state[1])))
    best_next_action = np.argmax(Q_table[next_state[0], next_state[1]])
    Q_table[state[0], state[1], action] += alpha * (reward + gamma * Q_table[next_state[0], next_state[1], best_next_action] - Q_table[state[0], state[1], action])

# Objectif à atteindre
goal_x = 570
goal_y = 75

def calculer_récompenses(x, y, previous_x, previous_y, distance_to_goal, previous_distance_to_goal):
    global objectif_atteint
    global mort
    
    reward = 0  # Initialisation

    perso_rect = pygame.Rect(x, y, LARGEUR_PERSO, HAUTEUR_PERSO)

    if perso_rect.colliderect(objectif):
        objectif_atteint = True
        reward += 1000  # Ajoute au lieu d'écraser

    for d in danger:
        if perso_rect.colliderect(d):
            mort = True
            #print("Mort")
            reward -= 100

    for obj in objectifs_intermediaires:
        if perso_rect.colliderect(obj):
            objectifs_intermediaires.remove(obj)
            reward += 10  # Ajoute au lieu d'écraser

    if distance_to_goal < previous_distance_to_goal:
        reward += 2
    else:
        reward -= 2

    if y // 30 == previous_y // 30:
        reward -= 10
    
    if x // 100 == previous_x // 100:
        reward -= 10
    

    # Calcul de la distance uniquement si l'objectif final n'est pas atteint
    if not objectif_atteint:
        distance_to_goal = abs(x - goal_x) + abs(y - goal_y)
        reward -= 1  # Pénalité constante pour éviter de stagner

    return reward

def reset_joueur(x_perso, y_perso, temps, temps_limite=5000, joueur_reinitialise=False):
    if temps > temps_limite and not joueur_reinitialise:
        x_perso, y_perso = 100, HAUTEUR - HAUTEUR_PERSO - 10  # Position de départ
        temps = 0
        joueur_reinitialise = True
        print("Temps écoulé, réinitialisation du joueur.")
    elif objectif_atteint:  # Quand l'objectif est atteint, réinitialiser le joueur
        x_perso, y_perso = 100, HAUTEUR - HAUTEUR_PERSO - 10  # Position de départ
        temps = 0
        joueur_reinitialise = False  # Réinitialiser pour permettre d'autres resets
        print("Objectif atteint, réinitialisation du joueur.")
    joueur_reinitialise = False   
    return x_perso, y_perso, temps, joueur_reinitialise

# Boucle principale
def main():
    global objectif_atteint, victoire, FPS, mort, mort_compteur
    x_perso, y_perso = 100, HAUTEUR - HAUTEUR_PERSO - 10
    vitesse_y = 0
    saut = False
    clock = pygame.time.Clock()
    running = True
    temps = 0
    compteur_action = 0
    action_courante = random.choice(actions)
    duree_action = 15
    mort = False
    joueur_reinitialise = False  # Variable pour contrôler la réinitialisation
    mort_compteur = 0

    while running:
        temps += 1
        pos_souris = pygame.mouse.get_pos()
        previous_x = x_perso
        previous_y = y_perso
        distance_to_goal = abs(x_perso - goal_x) + abs(y_perso - goal_y)
        previous_distance_to_goal = distance_to_goal

        # Réinitialiser le joueur si nécessaire
        x_perso, y_perso, temps, joueur_reinitialise = reset_joueur(x_perso, y_perso, temps, joueur_reinitialise=joueur_reinitialise)
        
        # Sélection de l'action
        state = (x_perso // 10, y_perso // 10)
        if compteur_action == 0:
            action_courante = choisir_action(state)
            compteur_action = duree_action
        action_index = action_courante
        compteur_action -= 1
        deplacement_x, saut_action = actions[action_index]

        # Déplacement
        x_perso += deplacement_x * vitesse_perso
        if saut_action and not saut:
            saut = True
            vitesse_y = -vitesse_saut

        # Gestion événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Changer les FPS lorsque la touche espace est pressée
                    if FPS == FPS_60:
                        FPS = FPS_50000
                    else:
                        FPS = FPS_60
                elif event.key == pygame.K_p:  # Mettre en pause et afficher la Q-table
                    paused = True
                    afficher_q_table(state)
                    while paused:
                        for pause_event in pygame.event.get():
                            if pause_event.type == pygame.QUIT:
                                running = False
                                paused = False
                            elif pause_event.type == pygame.KEYDOWN:
                                if pause_event.key == pygame.K_p:  # Reprendre avec 'P'
                                    paused = False

        # Gravité
        vitesse_y += gravite
        y_perso += vitesse_y

        # Vérification des limites de l'écran
        if x_perso < 0:
            reward = -50
            x_perso = 0
        elif x_perso + LARGEUR_PERSO > LARGEUR:
            reward = -50
            x_perso = LARGEUR - LARGEUR_PERSO
        if y_perso < 0:
            reward = -50
            y_perso = 0
        elif y_perso + HAUTEUR_PERSO > HAUTEUR:
            reward = -50
            y_perso = HAUTEUR - HAUTEUR_PERSO

        # Collisions
        perso_rect = pygame.Rect(x_perso, y_perso, LARGEUR_PERSO, HAUTEUR_PERSO)
        for platforme in platformes:
            if perso_rect.colliderect(platforme):
                if vitesse_y > 0:
                    y_perso = platforme.top - HAUTEUR_PERSO
                    vitesse_y = 0
                    saut = False

        # Récompense et mise à jour Q-table
        reward = calculer_récompenses(x_perso, y_perso, previous_x, previous_y, distance_to_goal, previous_distance_to_goal)
        next_state = (x_perso // 10, y_perso // 10)
        mettre_a_jour_Q(state, action_index, reward, next_state)
        distance_to_goal = abs(x_perso - goal_x) + abs(y_perso - goal_y)

        # Vérification victoire
        if objectif_atteint:
            objectif_atteint = False
            victoire += 1
            temps_victoires.append(temps)
            afficher_statistiques(temps, state)  # Affichage des stats
            temps = 0
            x_perso, y_perso = 100, HAUTEUR - HAUTEUR_PERSO - 10

        if mort:
            mort = False
            mort_compteur += 1
            temps = 0
            x_perso, y_perso = 100, HAUTEUR - HAUTEUR_PERSO - 10
        
        # Dessin
        fenetre.fill((0, 0, 0))
        pygame.draw.circle(fenetre, COULEUR_PERSONNAGE, (x_perso + LARGEUR_PERSO // 2, y_perso + HAUTEUR_PERSO // 2), LARGEUR_PERSO // 2)
        for platforme in platformes:
            pygame.draw.rect(fenetre, VERT_FONCE, platforme)
        pygame.draw.circle(fenetre, BLEU, (objectif.x + 10, objectif.y + 10), 10)
        for obj in objectifs_intermediaires:
            pygame.draw.circle(fenetre, (255, 215, 0), (obj.x + 7, obj.y + 7), 7)
        for d in danger:
            pygame.draw.rect(fenetre, (255, 0, 0), d)

        # Affichage du texte
        font = pygame.font.Font(None, 36)
        texte_victoire = font.render(f"Victoire : {victoire}", True, (255, 255, 255))
        fenetre.blit(texte_victoire, (10, 10))
        texte_mort = font.render(f"Mort : {mort_compteur}", True, (255, 255, 255))
        fenetre.blit(texte_mort, (10, 30))
        
        # Affiche les coordonnées de la souris en haut à gauche
        texte_coord = font.render(f"X: {pos_souris[0]} Y: {pos_souris[1]}", True, (255,255,255))
        fenetre.blit(texte_coord, (10, 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
