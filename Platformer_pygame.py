import pygame
import math

# Paramètres de base
pygame.init()
pygame.mixer.init()
LARGEUR = 800
HAUTEUR = 600
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Platformer jouable")

# Paramètre du personnage
LARGEUR_PERSO = 50
HAUTEUR_PERSO = 50
vitesse_perso = 5
vitesse_saut = 18
gravite = 1

# Couleurs
C1 = (135,206,235) #Bleu ciel (haut)
C2 = (25,25,112) #Bleu nuit (bas)
VERT_FONCE = (34, 139, 34)
VERT_CLAIR = (50,205,50)
BLEU = (25, 25, 200)
COULEUR_PERSONNAGE = (255, 69, 0)


# Platformes (x, y, largeur, hauteur)
platformes = [
    pygame.Rect(0, HAUTEUR - 10, LARGEUR, 10),  # Sol
    pygame.Rect(200, 450, 200, 10),  # Platforme 1
    pygame.Rect(500, 350, 200, 10),  # Platforme 2
    pygame.Rect(700, 250, 100, 10)   # Platforme 3
]

# Objectif
objectif = pygame.Rect(750, 200, 20, 20)

#Fonction pour dessiner le fond avec un dégradé de bleu
def dessiner_fond():
    for i in range(HAUTEUR):
        couleur_inter = (
            C1[0] + (C2[0] - C1[0])*i//HAUTEUR,
            C1[1] + (C2[1] - C1[1])*i//HAUTEUR,
            C1[2] + (C2[2] - C1[2])*i//HAUTEUR)
        pygame.draw.line(fenetre, couleur_inter, (0,i), (LARGEUR,i))

# Fonction pour dessiner le personnage sous forme de cercle
def dessiner_perso(x, y):
    pygame.draw.circle(fenetre, COULEUR_PERSONNAGE, (x + LARGEUR_PERSO // 2, y + HAUTEUR_PERSO // 2), LARGEUR_PERSO//2)  # Surface, couleur, dimensions et positions, (épaisseur du contour = optionnel)

# Fonction pour dessiner les plateformes avec effet 3D
def dessiner_platformes():
    for platforme in platformes:
        pygame.draw.rect(fenetre, VERT_FONCE, platforme) #On dessine d'abord les platformes en vert foncé
        pygame.draw.line(fenetre, VERT_CLAIR, (platforme.x, platforme.y), (platforme.x + platforme.width, platforme.y), 3) #On rajoute un trait clair au dessus

# Fonction pour dessiner l'objectif avec un cercle qui pulse
def dessiner_objectif(temps):
    taille_objectif = 10 + 3 * math.sin(temps*0.1) #Fait varier le cercle entre -3 et 3
    pygame.draw.circle(fenetre, BLEU, (objectif.x + 10, objectif.y + 10), int(taille_objectif))



# Boucle principale
def main():
    x_perso, y_perso= 100, HAUTEUR - HAUTEUR_PERSO - 10
    vitesse_y = 0
    victoire = 0
    saut = False
    clock = pygame.time.Clock()
    running = True
    temps = 0

    while running:
        dessiner_fond()
        temps += 1

        # Gestion des évènements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Si le croix de la fenetre est appuyé
                running = False

        # Gestion des touches
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT]:
            x_perso -= vitesse_perso  # Si flèche gauche pressé, la vitesse augmente dans le négatif
        if touches[pygame.K_RIGHT]:
            x_perso += vitesse_perso  # Accéleration si flèche droite pressé
        if touches[pygame.K_UP] and not saut:  # Saut si touche le sol
            saut = True
            vitesse_y = -vitesse_saut #Fait sauter le personnage (annule les effets de la gravité)

        # Appliquer la gravité
        vitesse_y += gravite #Vitesse y diminue
        y_perso += vitesse_y #Ramène le perso vers le sol
        
        # Vérification des collisions avec les plateformes
        perso_rect = pygame.Rect(x_perso, y_perso, LARGEUR_PERSO, HAUTEUR_PERSO)
        on_platforme = False

        for platforme in platformes:
            if perso_rect.colliderect(platforme):
                if vitesse_y > 0:  # Si on tombe on se pose sur la platforme
                    y_perso = platforme.top - HAUTEUR_PERSO
                    vitesse_y = 0
                    saut = False
                    on_platforme = True
                """elif vitesse_y < 0:  # Si on monte on frappe le plafond
                    y_perso = platforme.bottom
                    vitesse_y = 0"""

        #Vérification que le personnage ne sortent pas de l'écran
        if x_perso < 0 or x_perso > LARGEUR or y_perso < 0 or y_perso > HAUTEUR:
            
            x_perso, y_perso= 100, HAUTEUR - HAUTEUR_PERSO - 10


        #Verification de victoire
        if perso_rect.colliderect(objectif):
            victoire += 1
            x_perso, y_perso= 100, HAUTEUR - HAUTEUR_PERSO - 10
            

        # Dessiner les éléments du jeu
        dessiner_perso(x_perso, y_perso)
        dessiner_platformes()
        dessiner_objectif(temps)

        #Afficher le texte
        font = pygame.font.Font(None, 36) #Police de taille 36
        texte_victoire = font.render(f"Victoire : {victoire}", True, (0,0,0))
        fenetre.blit(texte_victoire, (10, 10))

        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main()