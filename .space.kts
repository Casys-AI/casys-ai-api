job("Qodana") {
  startOn {
    gitPush {
      anyBranchMatching {
        +"main"
        +"SMA-11"
      }
    }
    codeReviewOpened{}
  }
  container("jetbrains/qodana-python-community") {
    env["QODANA_TOKEN"] = "{{ project:qodana-token }}"
    shellScript {
      content = "qodana"
    }
  }
}