job("Qodana") {
  startOn {
    gitPush {
      anyBranchMatching {
        +"master"
      }
    }
    codeReviewOpened{}
  }
  container("jetbrains/qodana-python") {
    env["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcmdhbml6YXRpb24iOiJBbXFORSIsInByb2plY3QiOiIzZTlsRCIsInRva2VuIjoiQW04RTIifQ.TVhZfjESIHhoynXcgWtDc4R4A8sE-ZJQewQkgzYTSPg"] = "{{ project:qodana-token }}"
    shellScript {
      content = "qodana"
    }
  }
}