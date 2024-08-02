```mermaid
requirementDiagram
    requirement mainReq {
        id: 1
        text: Develop a Digital Twin of a coffee machine using Simcenter Amesim
        risk: High
        verification: analysis
    }

    functionalRequirement modelComponents {
        id: 1.1
        text: Model components of the coffee machine
        risk: Medium
        verification: analysis
    }

    functionalRequirement intermediateDetailModels {
        id: 1.1.1
        text: Create intermediate-detail models for each component
        risk: Medium
        verification: analysis
    }

    functionalRequirement controlModule {
        id: 1.1.2
        text: Add a control module to the coffee machine
        risk: Medium
        verification: analysis
    }

    functionalRequirement controlLogic {
        id: 1.1.3
        text: Program control logic using a state chart
        risk: Medium
        verification: analysis
    }

    performanceRequirement analyzeBehavior {
        id: 1.2
        text: Analyze physical behavior, energy consumption, and production rates
        risk: Medium
        verification: analysis
    }

    functionalRequirement simpleModels {
        id: 1.3
        text: Start with simple functional models and verify them
        risk: Low
        verification: test
    }

    functionalRequirement physicsBasedModels {
        id: 1.4
        text: Transition to physics-based modeling
        risk: Medium
        verification: analysis
    }

    functionalRequirement assembleMachine {
        id: 1.5
        text: Assemble the complete coffee machine
        risk: Medium
        verification: demonstration
    }

    functionalRequirement interactiveElements {
        id: 1.6
        text: Incorporate interactive elements to simulate real usage
        risk: Medium
        verification: demonstration
    }

    mainReq contains modelComponents
    mainReq contains analyzeBehavior
    mainReq contains simpleModels
    mainReq contains physicsBasedModels
    mainReq contains assembleMachine
    mainReq contains interactiveElements

    modelComponents contains intermediateDetailModels
    modelComponents contains controlModule
    modelComponents contains controlLogic

    controlModule satisfies controlLogic
```