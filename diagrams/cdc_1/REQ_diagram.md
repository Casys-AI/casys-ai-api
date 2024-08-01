```mermaid
requirementDiagram
    requirement mainReq {
        id: RQ-001
        text: Develop a Digital Twin of a coffee machine
        risk: High
        verification: analysis
    }

    functionalRequirement architectureReq {
        id: RQ-002
        text: Define product architecture
        risk: Medium
        verification: analysis
    }

    functionalRequirement componentSizingReq {
        id: RQ-003
        text: Size components
        risk: Medium
        verification: analysis
    }

    functionalRequirement physicalModelsReq {
        id: RQ-004
        text: Provide physical plant models for control development
        risk: High
        verification: analysis
    }

    performanceRequirement costReductionReq {
        id: RQ-005
        text: Reduce development costs and risks
        risk: High
        verification: analysis
    }

    functionalRequirement componentModelingReq {
        id: RQ-006
        text: Model individual components of the coffee machine
        risk: Medium
        verification: analysis
    }

    functionalRequirement controlAlgorithmReq {
        id: RQ-007
        text: Build a simple control algorithm
        risk: Medium
        verification: analysis
    }

    performanceRequirement energyConsumptionReq {
        id: RQ-008
        text: Assess energy consumption
        risk: Medium
        verification: analysis
    }

    performanceRequirement productionRatesReq {
        id: RQ-009
        text: Assess production rates
        risk: Medium
        verification: analysis
    }

    functionalRequirement interactiveElementsReq {
        id: RQ-010
        text: Incorporate interactive elements
        risk: Low
        verification: analysis
    }

    functionalRequirement stateChartReq {
        id: RQ-011
        text: Use a state chart to program control logic
        risk: Medium
        verification: analysis
    }

    mainReq contains architectureReq
    mainReq contains componentSizingReq
    mainReq contains physicalModelsReq
    mainReq contains costReductionReq
    mainReq contains componentModelingReq
    mainReq contains controlAlgorithmReq
    mainReq contains energyConsumptionReq
    mainReq contains productionRatesReq
    mainReq contains interactiveElementsReq
    mainReq contains stateChartReq

    architectureReq derives componentSizingReq
    architectureReq derives physicalModelsReq

    componentModelingReq satisfies physicalModelsReq
```