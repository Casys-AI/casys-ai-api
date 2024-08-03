```mermaid
requirementDiagram
    requirement mainReq {
        id: R1
        text: The crushing mill transforms coffee beans into powder.
        risk: High
        verification: analysis
    }

    functionalRequirement modelReq {
        id: R1.1
        text: The model should include rotational inertia with friction driven by a speed source or motor.
        risk: Medium
        verification: analysis
    }

    functionalRequirement controlReq {
        id: R1.2
        text: The model should include a control for constant rotary speed.
        risk: Medium
        verification: analysis
    }

    functionalRequirement lagReq {
        id: R1.3
        text: The model should include a first-order lag to prevent torque peaks.
        risk: Medium
        verification: analysis
    }

    functionalRequirement gearReq {
        id: R1.4
        text: The model should include a speed-reducing gear.
        risk: Low
        verification: analysis
    }

    functionalRequirement springDamperReq {
        id: R1.5
        text: The model should include a rotational spring/damper.
        risk: Low
        verification: analysis
    }

    functionalRequirement frictionReq {
        id: R1.6
        text: The model should include friction elements.
        risk: Low
        verification: analysis
    }

    functionalRequirement energySensorReq {
        id: R1.7
        text: The model should include an energy sensor.
        risk: Low
        verification: analysis
    }

    performanceRequirement motorEnhanceReq {
        id: R1.8
        text: Enhancing the model with an electrical motor and speed control can account for motor dynamics and heat generation.
        risk: Medium
        verification: analysis
    }

    performanceRequirement motorTempReq {
        id: R1.8.1
        text: Motor temperature should be a key parameter.
        risk: Medium
        verification: analysis
    }

    mainReq contains modelReq
    mainReq contains controlReq
    mainReq contains lagReq
    mainReq contains gearReq
    mainReq contains springDamperReq
    mainReq contains frictionReq
    mainReq contains energySensorReq
    mainReq contains motorEnhanceReq
    motorEnhanceReq contains motorTempReq

    motorEnhanceReq derives modelReq
    motorEnhanceReq derives controlReq
    motorEnhanceReq derives lagReq
    motorEnhanceReq derives gearReq
    motorEnhanceReq derives springDamperReq
    motorEnhanceReq derives frictionReq
    motorEnhanceReq derives energySensorReq

    motorEnhanceReq satisfies mainReq
```