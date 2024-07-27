```mermaid
requirementDiagram
    requirement mainReq {
        id: RQ-001
        text: The crushing mill transforms coffee beans into powder
        risk: High
        verification: analysis
    }

    functionalRequirement energyConsumptionAnalysis {
        id: RQ-002
        text: Simplified model for energy consumption analysis
        risk: Medium
        verification: analysis
    }

    performanceRequirement constantRotarySpeed {
        id: RQ-003
        text: Control for constant rotary speed
        risk: Medium
        verification: test
    }

    performanceRequirement firstOrderLag {
        id: RQ-004
        text: First-order lag to prevent torque peaks
        risk: Low
        verification: analysis
    }

    functionalRequirement motorIcon {
        id: RQ-005
        text: Motor icon for signal conversion
        risk: Low
        verification: inspection
    }

    functionalRequirement speedReducingGear {
        id: RQ-006
        text: Speed-reducing gear
        risk: Low
        verification: inspection
    }

    functionalRequirement rotationalSpringDamper {
        id: RQ-007
        text: Rotational spring/damper
        risk: Low
        verification: inspection
    }

    functionalRequirement frictionElements {
        id: RQ-008
        text: Friction elements
        risk: Low
        verification: inspection
    }

    functionalRequirement energySensor {
        id: RQ-009
        text: Energy sensor
        risk: Low
        verification: inspection
    }

    functionalRequirement enhancedModel {
        id: RQ-010
        text: Enhanced model with electrical motor and speed control
        risk: Medium
        verification: analysis
    }

    performanceRequirement motorDynamics {
        id: RQ-011
        text: Account for motor dynamics and heat generation
        risk: Medium
        verification: analysis
    }

    performanceRequirement temperatureParameter {
        id: RQ-012
        text: Temperature as a key parameter
        risk: Medium
        verification: test
    }

    mainReq --|> energyConsumptionAnalysis
    energyConsumptionAnalysis --|> constantRotarySpeed
    energyConsumptionAnalysis --|> firstOrderLag
    energyConsumptionAnalysis --|> motorIcon
    energyConsumptionAnalysis --|> speedReducingGear
    energyConsumptionAnalysis --|> rotationalSpringDamper
    energyConsumptionAnalysis --|> frictionElements
    energyConsumptionAnalysis --|> energySensor
    energyConsumptionAnalysis --|> enhancedModel
    enhancedModel --|> motorDynamics
    enhancedModel --|> temperatureParameter

    constantRotarySpeed -->|satisfies| mainReq
    motorDynamics -->|derives| enhancedModel
    temperatureParameter -->|derives| enhancedModel
```