```mermaid
requirementDiagram
    requirement mainReq {
        id: RQ-001
        text: Develop a Digital Twin of a coffee machine
        risk: High
        verification: analysis
    }

    functionalRequirement productArchitecture {
        id: RQ-002
        text: Define product architecture
        risk: Medium
        verification: analysis
    }
    mainReq --|> productArchitecture

    functionalRequirement componentSizing {
        id: RQ-003
        text: Size components
        risk: Medium
        verification: analysis
    }
    mainReq --|> componentSizing

    functionalRequirement physicalPlantModels {
        id: RQ-004
        text: Provide physical plant models for control development
        risk: High
        verification: analysis
    }
    mainReq --|> physicalPlantModels

    functionalRequirement modelComponents {
        id: RQ-005
        text: Model individual components
        risk: Medium
        verification: analysis
    }
    mainReq --|> modelComponents

    performanceRequirement assessBehavior {
        id: RQ-006
        text: Assess physical behavior, energy consumption, and production rates
        risk: Medium
        verification: analysis
    }
    modelComponents --|> assessBehavior

    functionalRequirement assembleMachine {
        id: RQ-007
        text: Assemble the complete coffee machine
        risk: Medium
        verification: analysis
    }
    mainReq --|> assembleMachine

    functionalRequirement controlModule {
        id: RQ-008
        text: Incorporate a control module
        risk: High
        verification: analysis
    }
    assembleMachine --|> controlModule

    functionalRequirement interactiveElements {
        id: RQ-009
        text: Add interactive elements to simulate real usage
        risk: Medium
        verification: analysis
    }
    assembleMachine --|> interactiveElements

    functionalRequirement stateChart {
        id: RQ-010
        text: Use a state chart to program the control logic
        risk: Medium
        verification: analysis
    }
    interactiveElements --|> stateChart

    performanceRequirement waterHeating {
        id: RQ-011
        text: Ensure efficient water heating
        risk: High
        verification: test
    }
    mainReq --|> waterHeating

    performanceRequirement pressureControl {
        id: RQ-012
        text: Maintain optimal pressure control
        risk: High
        verification: test
    }
    mainReq --|> pressureControl

    performanceRequirement userInterface {
        id: RQ-013
        text: Provide an intuitive user interface
        risk: Medium
        verification: inspection
    }
    mainReq --|> userInterface

    performanceRequirement coffeeQuality {
        id: RQ-014
        text: Ensure high coffee quality
        risk: High
        verification: test
    }
    mainReq --|> coffeeQuality

    componentSizing --|> waterHeating
    componentSizing --|> pressureControl
    controlModule --|> userInterface
    controlModule --|> coffeeQuality

    physicalPlantModels --|> waterHeating
    physicalPlantModels --|> pressureControl
    physicalPlantModels --|> coffeeQuality

    modelComponents --|> waterHeating
    modelComponents --|> pressureControl
    modelComponents --|> coffeeQuality

    interactiveElements --|> userInterface
    interactiveElements --|> coffeeQuality
```