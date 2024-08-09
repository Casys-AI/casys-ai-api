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
    env["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcmdhbml6YXRpb24iOiJBbXFORSIsInByb2plY3QiOiJBTkQ1MSIsInRva2VuIjoiQU95TzYifQ.Yn33UPfH9FqZNcNX4smyJkvxWtvpjgWCuUYbgUWHYvg"] = "{{ project:qodana-token }}"
    shellScript {
      content = "qodana"
    }
  }
}