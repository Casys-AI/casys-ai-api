job("Qodana") {
  startOn {
    gitPush {
      anyBranchMatching {
        +"main"
      }
    }
    codeReviewOpened{}
  }
  container("jetbrains/qodana-python-community") {
    env["QODANA_TOKEN"] = "{{ project:qodana-token }}"
    shellScript {
      content = """
        # Activer l'environnement virtuel
        source venv/bin/activate

        # Vérifier que l'environnement virtuel est bien activé
        which python
        python --version

        # Installer les dépendances (si nécessaire)
        pip install -r requirements.txt

        # Exécuter Qodana
        qodana --baseline qodana.sarif.json
      """
    }
  }
}