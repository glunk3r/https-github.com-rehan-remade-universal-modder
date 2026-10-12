# Calendrier de l'Avent

Une petite page autonome et adaptée aux téléphones en français pour préparer un calendrier de Noël, ajouter une image, un message, une décoration et une forme à chacune des 24 cases, puis partager un lien de consultation. Les commandes tactiles, le choix de photos depuis le téléphone et les éditeurs défilants permettent d'effectuer toutes les personnalisations sur petit écran. Chaque case peut prendre l'une de dix formes (arrondie, carrée, ronde, arche, ovale, losange, hexagone, étoile, cœur ou triangle) et dispose d'un aperçu animé dans l'éditeur. Choisis aussi une animation générale parmi neuf styles (pivot, grande ouverture, trappe, envol, zoom, disparition scintillante, glissement, rideau ou rebond) et teste-la dans l'aperçu avant de l'appliquer. À l'ouverture, des motifs festifs jaillissent autour de la porte. Le lien contient une copie du calendrier : la personne qui le reçoit peut ouvrir les surprises, mais son interface ne lui permet pas de les modifier.

L’éditeur **Décorer mon calendrier** permet aussi de charger une photo depuis l’ordinateur pour remplacer l’illustration du bandeau, puis de choisir son côté (gauche/droite), sa largeur, son zoom et le cadrage horizontal et vertical. Tous ces réglages sont visibles en direct; tu peux retirer la photo pour retrouver l’illustration d’origine. La photo redimensionnée et son cadrage sont sauvegardés dans le calendrier partagé. Tu peux aussi choisir une écriture pour les titres et les numéros, et modifier la phrase sous le titre. Le titre principal se modifie directement sur la page, et les textes des surprises se changent en ouvrant les cases.

## Lancer la page

Depuis ce dossier, lance le serveur statique Python :

```bash
python -m http.server 8000
```

Ouvre ensuite <http://localhost:8000>. Cela sert uniquement à prévisualiser le calendrier sur ton appareil; les adresses `localhost` ne sont pas accessibles à tes proches. Il n'y a ni dépendance à installer ni compte à créer.

### Publier pour partager les liens

Après avoir intégré ces fichiers à `main`, active **Settings → Pages → Build and deployment → Source → GitHub Actions** dans le dépôt, puis lance l'action **Advent calendar Pages** dans l'onglet **Actions** (ou pousse une modification du calendrier sur `main`). Cela publie la page à <https://rehan-remade.github.io/universal-modder/>. Crée le lien partagé depuis cette adresse publique; un lien créé depuis l'aperçu local ne peut pas fonctionner sur l'appareil d'un destinataire.

## Créer et partager

1. Choisis **Décorer mon calendrier** pour charger ta photo et régler son côté, sa largeur, son zoom et son cadrage. Tu peux aussi changer les écritures et la phrase d’introduction, ainsi que le fond de la page, les couleurs, la forme, le motif et l'animation d'ouverture générale des cases. L'aperçu permet de tester chacune des neuf animations. Tu peux choisir les piques ♠ comme motif général. Le choix « garder les décorations propres à chaque case » conserve les motifs individuels.
2. Utilise **Mélanger les cases** pour changer leur disposition sans séparer les numéros de leurs surprises; le mélange est conservé dans le brouillon et le lien partagé. **Remettre dans l'ordre** restaure l'ordre des dates. Ouvre une case pour ajouter un titre, un message, une image, ses couleurs, sa décoration, sa forme et son animation d'ouverture. Choisis **Suivre l'animation générale du calendrier** pour hériter du réglage général, ou une animation différente pour cette case seulement. Le bouton **Ouvrir la porte** prévisualise l'animation choisie.
3. Modifie le titre du calendrier en cliquant dessus, puis choisis **Créer un lien**.
4. Copie le lien et envoie-le à la personne qui recevra le calendrier.
5. En ouvrant ce lien, cette personne découvre les cases en lecture seule. Du 1er au 24 décembre, chaque case reste verrouillée jusqu'à son jour; les cases déjà ouvertes restent accessibles et peuvent être revues. En dehors de décembre, seules les cases déjà ouvertes restent accessibles. La progression est mémorisée dans le navigateur du lecteur.

Les brouillons du créateur sont enregistrés dans le stockage local du navigateur. Les images sont intégrées au lien (les photos sont réduites pour limiter sa taille). Le lien n'est pas un identifiant hébergé : il embarque une copie des surprises. Toute personne qui le possède peut consulter cette copie ; aucune modification faite par un lecteur ne peut être renvoyée au créateur. La page doit être publiée sur un hébergement web public pour que le lien soit accessible à d'autres personnes. L'application refuse de fabriquer un faux lien depuis `file://`, `localhost` ou une adresse IP privée; publie d'abord le dossier, puis crée le lien depuis l'adresse publique du site.

Les données du calendrier dans le lien sont compressées avec gzip dans les navigateurs récents. La page ne transmet ni ne stocke les données sur un serveur.
