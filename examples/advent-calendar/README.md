# Calendrier de l'Avent

Une petite page autonome et adaptée aux téléphones en français pour préparer un calendrier de Noël, ajouter une image, un message, une décoration et une forme à chacune des 24 cases, puis partager un lien de consultation. Les commandes tactiles, le choix de photos depuis le téléphone et les éditeurs défilants permettent d'effectuer toutes les personnalisations sur petit écran. Chaque case peut prendre l'une de dix formes (arrondie, carrée, ronde, arche, ovale, losange, hexagone, étoile, cœur ou triangle) et dispose d'un aperçu animé dans l'éditeur. Choisis aussi une animation générale parmi neuf styles (pivot, grande ouverture, trappe, envol, zoom, disparition scintillante, glissement, rideau ou rebond) et teste-la dans l'aperçu avant de l'appliquer. À l'ouverture, des motifs festifs jaillissent autour de la porte. Le lien contient une copie du calendrier : la personne qui le reçoit peut ouvrir les surprises, mais son interface ne lui permet pas de les modifier.

L’éditeur **Décorer mon calendrier** permet aussi de charger une photo depuis l’ordinateur pour remplacer l’illustration du bandeau, puis de choisir son côté (gauche/droite), sa largeur, son zoom et le cadrage horizontal et vertical. Tous ces réglages sont visibles en direct; tu peux retirer la photo pour retrouver l’illustration d’origine. La photo redimensionnée et son cadrage sont sauvegardés dans le calendrier partagé. Tu peux aussi choisir une écriture pour les titres et les numéros, et modifier la phrase sous le titre. Le titre principal se modifie directement sur la page, et les textes des surprises se changent en ouvrant les cases.

## Lancer la page

Depuis ce dossier, lance le serveur statique Python :

```bash
python -m http.server 8000
```

Ouvre ensuite <http://localhost:8000>. Cela sert uniquement à prévisualiser le calendrier sur ton appareil; les adresses `localhost` ne sont pas accessibles à tes proches. Il n'y a ni dépendance à installer ni compte à créer.

### Page publique

La version actuellement publiée est accessible à <https://jeanchales13-beep.github.io/universal-modder/>. Ouvre cette adresse pour créer un lien que tes proches pourront consulter. Le lien est construit depuis cette URL publique et contient une copie du calendrier; chaque destinataire voit les surprises en lecture seule.

Cette page est une publication sur le fork de développement. Pour publier la version du dépôt source, intègre les fichiers à `main`, active **Settings → Pages → Build and deployment → Source → GitHub Actions** dans le dépôt source, puis lance l'action **Advent calendar Pages** dans l'onglet **Actions**. Elle sera alors publiée à <https://rehan-remade.github.io/universal-modder/>. Les liens créés depuis `localhost` ou `file://` sont refusés, car ils ne seraient pas accessibles aux destinataires.

### Activer les comptes créateur

Les comptes et leur sauvegarde en ligne utilisent Supabase; le projet doit être configuré par son propriétaire avant de pouvoir créer de vrais comptes.

1. Crée un projet Supabase, puis exécute le contenu de `supabase-schema.sql` dans son **SQL Editor**. La table et ses règles de sécurité garantissent qu'un compte ne possède qu'un seul calendrier et que seuls ses propriétaires peuvent le consulter ou le modifier.
2. Dans les paramètres API du projet Supabase, copie l'URL du projet et sa clé **publishable** (ou l'ancienne clé **anon/public**). Active **Email** dans les fournisseurs d'authentification Supabase; si la confirmation des nouveaux comptes est activée, configure l'envoi de courriels dans Supabase.
3. Remplace `url` et `anonKey` dans `account-config.js`, puis publie de nouveau le dossier du calendrier. Ces valeurs sont des identifiants publics utilisables dans un navigateur; n'y mets jamais la clé `service_role` ou une clé secrète.
4. La personne créatrice choisit **Mon compte**, puis **Créer mon compte**. Si la confirmation de courriel est activée dans Supabase, elle confirme son adresse avant de se connecter. À sa première connexion, le brouillon local devient son unique calendrier en ligne; un calendrier déjà enregistré pour ce compte remplace le brouillon local.

Sans URL et clé Supabase valides dans `account-config.js`, les champs d'inscription et de connexion sont masqués et l'application explique que les comptes doivent être activés par le propriétaire du site; la création d'un compte ne peut pas fonctionner. Ne partage pas la clé `service_role`, même si l'hébergement de la page est public.

## Créer et partager

1. Choisis **Décorer mon calendrier** pour charger ta photo et régler son côté, sa largeur, son zoom et son cadrage. Tu peux aussi changer les écritures et la phrase d’introduction, ainsi que le fond de la page, les couleurs, la forme, le motif et l'animation d'ouverture générale des cases. L'aperçu permet de tester chacune des neuf animations. Tu peux choisir les piques ♠ comme motif général. Le choix « garder les décorations propres à chaque case » conserve les motifs individuels.
2. Utilise **Mélanger les cases** pour changer leur disposition sans séparer les numéros de leurs surprises; le mélange est conservé dans le brouillon et le lien partagé. **Remettre dans l'ordre** restaure l'ordre des dates. Ouvre une case pour ajouter un titre, un message, une image, ses couleurs, sa décoration, sa forme et son animation d'ouverture. Choisis **Suivre l'animation générale du calendrier** pour hériter du réglage général, ou une animation différente pour cette case seulement. Le bouton **Ouvrir la porte** prévisualise l'animation choisie.
3. Modifie le titre du calendrier en cliquant dessus, puis choisis **Créer un lien**.
4. Copie le lien et envoie-le à la personne qui recevra le calendrier.
5. En ouvrant ce lien, cette personne découvre les cases en lecture seule. Du 1er au 24 décembre, chaque case reste verrouillée jusqu'à son jour; les cases déjà ouvertes restent accessibles et peuvent être revues. En dehors de décembre, seules les cases déjà ouvertes restent accessibles. La progression est mémorisée dans le navigateur du lecteur.

Sans compte configuré, le brouillon du créateur reste enregistré dans le stockage local du navigateur. Avec un compte Supabase, le même calendrier unique est sauvegardé en ligne et récupéré lors des connexions suivantes. Les images sont intégrées au lien (les photos sont réduites pour limiter sa taille). Le lien n'est pas un identifiant hébergé : il embarque une copie des surprises. Toute personne qui le possède peut consulter cette copie ; aucune modification faite par un lecteur ne peut être renvoyée au créateur. La page doit être publiée sur un hébergement web public pour que le lien soit accessible à d'autres personnes. L'application refuse de fabriquer un faux lien depuis `file://`, `localhost` ou une adresse IP privée; publie d'abord le dossier, puis crée le lien depuis l'adresse publique du site.

Les données du calendrier dans le lien sont compressées avec gzip dans les navigateurs récents. La page ne transmet ni ne stocke les données sur un serveur.
