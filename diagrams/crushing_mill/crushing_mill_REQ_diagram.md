```mermaid
requirementDiagram
    requirement mainReq {
        id: 1
        text: The coffee machine must efficiently transform coffee beans into powder and manage energy consumption.
        risk: High
        verifyMethod: analysis
    }

    functionalRequirement crushingMill {
        id: 1.1
        text: The crushing mill must transform coffee beans into powder.
        risk: High
        verifyMethod: analysis
    }

    performanceRequirement energyConsumption {
        id: 1.2
        text: The energy consumption of the coffee machine must be minimized.
        risk: Medium
        verifyMethod: analysis
    }

    functionalRequirement rotationalSpringDamper {
        id: 1.3
        text: The model must include a rotational spring/damper for causality.
        risk: Medium
        verifyMethod: analysis
    }

    functionalRequirement frictionElements {
        id: 1.4
        text: The model must include friction elements.
        risk: Medium
        verifyMethod: analysis
    }

    functionalRequirement controlRotarySpeed {
        id: 1.5
        text: The model must include a control for constant rotary speed.
        risk: Low
        verifyMethod: analysis
    }

    functionalRequirement motorIcon {
        id: 1.6
        text: The model must include a motor icon for signal transfer.
        risk: Low
        verifyMethod: analysis
    }

    functionalRequirement gearSpeedReduction {
        id: 1.7
        text: The model must include a gear for speed reduction.
        risk: Low
        verifyMethod: analysis
    }

    functionalRequirement energySensor {
        id: 1.8
        text: The model must include an energy sensor.
        risk: Low
        verifyMethod: analysis
    }

    functionalRequirement electricalMotor {
        id: 1.9
        text: The model can include an electrical motor with voltage supply and speed control.
        risk: Medium
        verifyMethod: analysis
    }

    mainReq contains crushingMill
    mainReq contains energyConsumption
    mainReq contains rotationalSpringDamper
    mainReq contains frictionElements
    mainReq contains controlRotarySpeed
    mainReq contains motorIcon
    mainReq contains gearSpeedReduction
    mainReq contains energySensor
    mainReq contains electricalMotor

    crushingMill derives rotationalSpringDamper
    crushingMill derives frictionElements
    crushingMill derives controlRotarySpeed
    crushingMill derives motorIcon
    crushingMill derives gearSpeedReduction
    crushingMill derives energySensor
    crushingMill derives electricalMotor

    energyConsumption satisfies mainReq
```