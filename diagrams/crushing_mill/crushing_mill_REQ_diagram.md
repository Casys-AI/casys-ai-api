```mermaid
requirementDiagram
    requirement mainReq {
        id: RQ-001
        text: The crushing mill transforms coffee beans into coffee powder.
        risk: High
        verification: analysis
    }

    functionalRequirement energyConsumptionAnalysis {
        id: RQ-002
        text: For energy consumption analysis, a simpler model using rotational inertia with friction driven by a speed source or motor is sufficient.
        risk: Medium
        verification: analysis
    }

    functionalRequirement constantRotarySpeedControl {
        id: RQ-003
        text: The model includes a control for constant rotary speed.
        risk: Medium
        verification: test
    }

    functionalRequirement motorIconSignalTransfer {
        id: RQ-004
        text: The model includes a motor icon for signal transfer.
        risk: Low
        verification: inspection
    }

    functionalRequirement mechanicalGearSpeedReduction {
        id: RQ-005
        text: The model includes a mechanical gear for speed reduction.
        risk: Medium
        verification: test
    }

    functionalRequirement rotationalSpringDamper {
        id: RQ-006
        text: The model includes a rotational spring/damper.
        risk: Medium
        verification: test
    }

    functionalRequirement frictionElements {
        id: RQ-007
        text: The model includes friction elements.
        risk: Medium
        verification: test
    }

    functionalRequirement energySensor {
        id: RQ-008
        text: The model includes an energy sensor.
        risk: Low
        verification: inspection
    }

    performanceRequirement motorDynamicsHeatGeneration {
        id: RQ-009
        text: Enhancing the model with an electrical motor and speed control can account for motor dynamics and heat generation.
        risk: High
        verification: analysis
    }

    performanceRequirement motorTemperatureParameter {
        id: RQ-010
        text: Motor temperature as a potential process parameter.
        risk: Medium
        verification: analysis
    }

    mainReq contains energyConsumptionAnalysis
    mainReq contains constantRotarySpeedControl
    mainReq contains motorIconSignalTransfer
    mainReq contains mechanicalGearSpeedReduction
    mainReq contains rotationalSpringDamper
    mainReq contains frictionElements
    mainReq contains energySensor
    mainReq contains motorDynamicsHeatGeneration
    motorDynamicsHeatGeneration contains motorTemperatureParameter

    motorDynamicsHeatGeneration derives energyConsumptionAnalysis
    motorTemperatureParameter derives motorDynamicsHeatGeneration

    motorIconSignalTransfer satisfies constantRotarySpeedControl
```