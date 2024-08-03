```mermaid
requirementDiagram
    requirement mainReq {
        id: R1
        text: Develop a Digital Twin of a coffee machine
        risk: High
    }

    functionalRequirement modelComponents {
        id: R1.1
        text: Model individual components of the coffee machine
        risk: Medium
        verification: analysis
    }

    functionalRequirement assembleMachine {
        id: R1.2
        text: Assemble the complete coffee machine
        risk: Medium
        verification: demonstration
    }

    functionalRequirement controlModule {
        id: R1.3
        text: Incorporate a control module
        risk: Medium
        verification: analysis
    }

    performanceRequirement assessBehavior {
        id: R1.1.1
        text: Assess physical behavior, energy consumption, and production rates
        risk: Low
        verification: analysis
    }

    functionalRequirement simpleModels {
        id: R1.1.2
        text: Start with simple functional models and gradually add details
        risk: Low
        verification: analysis
    }

    functionalRequirement verifyModels {
        id: R1.1.3
        text: Verify models at each stage
        risk: Low
        verification: test
    }

    functionalRequirement interactiveElements {
        id: R1.3.1
        text: Add interactive elements to simulate real usage
        risk: Medium
        verification: demonstration
    }

    functionalRequirement stateChart {
        id: R1.3.2
        text: Use a state chart to program the control logic
        risk: Medium
        verification: analysis
    }

    mainReq contains modelComponents
    mainReq contains assembleMachine
    mainReq contains controlModule

    modelComponents contains assessBehavior
    modelComponents contains simpleModels
    modelComponents contains verifyModels

    controlModule contains interactiveElements
    controlModule contains stateChart

    modelComponents derives assessBehavior
    controlModule satisfies mainReq
```