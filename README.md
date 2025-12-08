## 🤖 Agent IA MongoDB (MCP)

Ce projet met en œuvre une architecture d'agent intelligent conçue pour orchestrer et répondre aux requêtes complexes des utilisateurs relatives à une base de données MongoDB. Le cœur de cette solution réside dans le mcp_client, l'orchestrateur, qui gère le flux de travail et distribue les tâches aux différents mcp_server spécialisés.


-----

## 🏗️ Architecture du Projet

Ce dépôt est structuré autour de trois composants principaux :

  * **`mcp_server/`**: Contient les implémentations des serveurs (ou agents spécifiques) qui gèrent des fonctionnalités distinctes. Par exemple, le serveur de base de données (déjà implémenté) se trouve ici.
  * **`mcp_client/`**: Le cerveau de l'application. C'est l'**orchestrateur** qui gère le flux de travail (`workflow`). Il reçoit les requêtes utilisateur et les distribue aux serveurs MCP appropriés.
  * **`user_interface/`**: Contient l'interface utilisateur Gradio permettant d'interagir facilement avec l'agent.

-----

## 🚀 Démarrage et Installation (Setup)

Suivez ces étapes pour démarrer l'ensemble du projet via Docker.

### Prérequis

Assurez-vous d'avoir [Docker](https://www.docker.com/get-started) et [Docker Compose](https://docs.docker.com/compose/install/) installés sur votre machine.

### Étape 1 : Construction et Lancement des Conteneurs

Exécutez la commande suivante à la racine du dépôt. Cette commande va construire les images nécessaires et lancer tous les services en mode détaché (`-d`).

```bash
docker-compose up -d --build
```

### Étape 2 : Accès aux Services

Une fois que tous les conteneurs sont opérationnels, vous pouvez accéder aux différents services :

1.  **Interface Utilisateur (Chatbot)** :

      * Ouvrez votre navigateur et accédez à : **`http://localhost:7860`**
      * Vous pouvez commencer à interagir avec l'Agent IA.

2.  **Documentation API (Swagger)** :

      * La documentation Swagger de l'API orchestrateur est disponible à l'adresse : **`http://localhost:5353/docs`**
      * Ceci est utile pour tester directement les endpoints de l'orchestrateur (`mcp_client`).

-----

## 👨‍💻 Ajouter un Nouveau Serveur MCP

Si vous souhaitez étendre les capacités de l'agent, vous devrez ajouter de nouveaux serveurs et les intégrer au client orchestrateur.

### 1\. Création de Nouveaux Outils (`tools/`)

Le dossier **`tools/`** est le lieu où vous implémentez les **fonctions spécifiques** que votre agent sera capable d'exécuter (ex: effectuer des calculs, appeler des services externes, etc.).

  * Créez de nouveaux fichiers et fonctions dans le dossier `tools/`.

### 2\. Implémentation du Nouveau Serveur MCP (`mcp_server/`)

Pour ajouter une nouvelle fonctionnalité, créez un nouveau serveur en vous inspirant du serveur de base de données déjà implémenté :

  * **Structure :** Copiez la structure du serveur de la base de données existant (ex: gestion des routes, communication avec le client).
  * **Logique :** Le nouveau serveur MCP devrait exposer des endpoints qui appellent les fonctions définies dans le dossier `tools/`.

### 3\. Mise à Jour de l'Orchestrateur (`mcp_client/`)

Le **`mcp_client`** est le point central de contrôle. Pour que le nouvel agent soit utilisé :

  * **Enregistrement :** Assurez-vous que le nouveau serveur MCP est correctement enregistré auprès du client.
  * **Workflow :** Mettez à jour le **flux de travail** (`workflow`) dans le `mcp_client`. Le workflow détermine la logique par laquelle le client décide quel serveur MCP (ou quelle séquence d'opérations) utiliser pour répondre à une requête utilisateur donnée.
