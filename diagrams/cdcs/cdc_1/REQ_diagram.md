```mermaid
requirementDiagram
    requirement mainReq {
        id: RQ-001
        text: Develop a Digital Twin of a coffee machine
        risk: High
        verification: analysis
    }

    functionalRequirement componentModeling {
        id: RQ-002
        text: Model individual components at an intermediate detail level
        risk: Medium
        verification: analysis
    }

    functionalRequirement physicalBehavior {
        id: RQ-003
        text: Assess physical behavior, energy consumption, and production rates
        risk: Medium
        verification: analysis
    }

    functionalRequirement libraries {
        id: RQ-004
        text: Use required libraries for simulation
        risk: Low
        verification: inspection
    }

    functionalRequirement simpleModels {
        id: RQ-005
        text: Start with simple functional models and verify them
        risk: Low
        verification: test
    }

    functionalRequirement completeAssembly {
        id: RQ-006
        text: Assemble the complete coffee machine and add a control module
        risk: Medium
        verification: demonstration
    }

    functionalRequirement interactiveElements {
        id: RQ-007
        text: Incorporate interactive elements and use a state chart for control logic
        risk: Medium
        verification: analysis
    }

    performanceRequirement waterHeating {
        id: RQ-008
        text: Ensure efficient water heating
        risk: High
        verification: test
    }

    performanceRequirement pressureControl {
        id: RQ-009
        text: Maintain optimal pressure control
        risk: High
        verification: test
    }

    performanceRequirement userInterface {
        id: RQ-010
        text: Provide an intuitive user interface
        risk: Medium
        verification: inspection
    }

    performanceRequirement coffeeQuality {
        id: RQ-011
        text: Ensure high coffee quality
        risk: High
        verification: demonstration
    }

    mainReq contains componentModeling
    mainReq contains physicalBehavior
    mainReq contains libraries
    mainReq contains simpleModels
    mainReq contains completeAssembly
    mainReq contains interactiveElements

    componentModeling derives physicalBehavior
    componentModeling derives libraries
    componentModeling derives simpleModels

    completeAssembly satisfies waterHeating
    completeAssembly satisfies pressureControl
    completeAssembly satisfies userInterface
    completeAssembly satisfies coffeeQuality
```