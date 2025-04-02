import pygame
import math
import numpy as np
import random

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
    pygame.Rect(200, 450, 200, 10),
    pygame.Rect(450, 350, 250, 10),
    pygame.Rect(700, 250, 100, 10)
]

# Objectif
objectif = pygame.Rect(750, 200, 20, 20)
objectif_atteint = False

# Objectifs intermédiaires
objectifs_intermediaires = [
    pygame.Rect(250, 430, 15, 15),
    pygame.Rect(550, 330, 15, 14),
]

# Q-learning paramètres
actions = [(0, 0), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1)]
gamma = 0.9
alpha = 0.15
epsilon = 0.2
states = (LARGEUR // 10, HAUTEUR // 10)
Q_table = np.zeros((states[0], states[1], len(actions)))

# Statistiques d'entraînement
victoire = 0
temps_victoires = []
FPS = 500000

# Fonction de suivi
def afficher_statistiques(temps_partie, state):
    if len(temps_victoires) > 0:
        moyenne_temps = sum(temps_victoires) / len(temps_victoires)
    else:
        moyenne_temps = 0

    valeur_Q_moyenne = np.mean(Q_table[state[0], state[1]])

    print(f"Victoires : {victoire} | Temps moyen : {moyenne_temps:.1f} frames | Q-table moy : {valeur_Q_moyenne:.2f}")

# Fonction d'apprentissage Q-learning
def choisir_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, len(actions) - 1)
    return np.argmax(Q_table[state[0], state[1]])

def mettre_a_jour_Q(state, action, reward, next_state):
    next_state = (min(states[0] - 1, max(0, next_state[0])),
                  min(states[1] - 1, max(0, next_state[1])))
    best_next_action = np.argmax(Q_table[next_state[0], next_state[1]])
    Q_table[state[0], state[1], action] += alpha * (reward + gamma * Q_table[next_state[0], next_state[1], best_next_action] - Q_table[state[0], state[1], action])

# Objectif à atteindre
goal_x = 750
goal_y = 200

def calculer_récompenses(x, y):
    global objectif_atteint
    perso_rect = pygame.Rect(x, y, LARGEUR_PERSO, HAUTEUR_PERSO)

    if perso_rect.colliderect(objectif):
        objectif_atteint = True
        return 50

    for obj in objectifs_intermediaires:
        if perso_rect.colliderect(obj):
            objectifs_intermediaires.remove(obj)
            return 10
    
    if x > 450 and y > 370 or x<15:
        return -20

    # Calcul de la distance entre la position actuelle et l'objectif
    distance_to_goal = abs(x - goal_x) + abs(y - goal_y)
    
    # Plus l'IA est proche de l'objectif, plus la récompense est élevée
    reward = 5 / (distance_to_goal + 1)  # +1 pour éviter la division par zéro

    return -1

# Boucle principale
def main():
    global objectif_atteint, victoire
    x_perso, y_perso = 100, HAUTEUR - HAUTEUR_PERSO - 10
    vitesse_y = 0
    saut = False
    clock = pygame.time.Clock()
    running = True
    temps = 0
    compteur_action = 0
    action_courante = random.choice(actions)
    duree_action = 15

    while running:
        temps += 1
        pos_souris = pygame.mouse.get_pos()

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
        reward = calculer_récompenses(x_perso, y_perso)
        next_state = (x_perso // 10, y_perso // 10)
        mettre_a_jour_Q(state, action_index, reward, next_state)

        # Vérification victoire
        if objectif_atteint:
            objectif_atteint = False
            victoire += 1
            temps_victoires.append(temps)
            afficher_statistiques(temps, state)  # Affichage des stats
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

        # Affichage du texte
        font = pygame.font.Font(None, 36)
        texte_victoire = font.render(f"Victoire : {victoire}", True, (255, 255, 255))
        fenetre.blit(texte_victoire, (10, 10))
        
        # Affiche les coordonnées de la souris en haut à gauche
        texte_coord = font.render(f"X: {pos_souris[0]} Y: {pos_souris[1]}", True, (255,255,255))
        fenetre.blit(texte_coord, (10, 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
