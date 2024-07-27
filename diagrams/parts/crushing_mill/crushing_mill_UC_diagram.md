```mermaid
%% SysML Use Case Diagram for Coffee Crushing Mill

%% Define actors
actor User
actor MaintenanceTechnician

%% Define use cases
usecase UC1 as "Transform Coffee Beans into Powder"
usecase UC2 as "Analyze Energy Consumption"
usecase UC3 as "Control Rotary Speed"
usecase UC4 as "Prevent Torque Peaks"
usecase UC5 as "Convert Signal"
usecase UC6 as "Reduce Speed"
usecase UC7 as "Dampen Rotation"
usecase UC8 as "Measure Energy"
usecase UC9 as "Enhance Model with Electrical Motor"
usecase UC10 as "Control Speed"
usecase UC11 as "Account for Motor Dynamics"
usecase UC12 as "Generate Heat"
usecase UC13 as "Monitor Temperature"
usecase UC14 as "Provide Results"

%% Define containment relationships
UC1 --> UC2
UC2 --> UC3
UC2 --> UC4
UC2 --> UC5
UC2 --> UC6
UC2 --> UC7
UC2 --> UC8
UC2 --> UC9
UC9 --> UC10
UC9 --> UC11
UC9 --> UC12
UC9 --> UC13
UC2 --> UC14

%% Define associations
User --> UC1
MaintenanceTechnician --> UC14
```

### Text Descriptions for Each Use Case

1. **UC1: Transform Coffee Beans into Powder**
   - **Description:** The primary function of the crushing mill, which involves transforming coffee beans into powder.

2. **UC2: Analyze Energy Consumption**
   - **Description:** Analyze the energy consumption of the crushing mill using a simplified model.

3. **UC3: Control Rotary Speed**
   - **Description:** Maintain a constant rotary speed in the crushing mill.

4. **UC4: Prevent Torque Peaks**
   - **Description:** Use a first-order lag to prevent torque peaks during the operation.

5. **UC5: Convert Signal**
   - **Description:** Use a motor icon to convert signals for the crushing mill.

6. **UC6: Reduce Speed**
   - **Description:** Implement a speed-reducing gear in the model.

7. **UC7: Dampen Rotation**
   - **Description:** Use a rotational spring/damper to dampen the rotation.

8. **UC8: Measure Energy**
   - **Description:** Include an energy sensor to measure the energy consumption.

9. **UC9: Enhance Model with Electrical Motor**
   - **Description:** Enhance the model by adding an electrical motor and speed control.

10. **UC10: Control Speed**
    - **Description:** Control the speed of the electrical motor.

11. **UC11: Account for Motor Dynamics**
    - **Description:** Consider the dynamics of the motor in the enhanced model.

12. **UC12: Generate Heat**
    - **Description:** Account for heat generation in the motor.

13. **UC13: Monitor Temperature**
    - **Description:** Monitor the temperature as a key parameter in the enhanced model.

14. **UC14: Provide Results**
    - **Description:** Provide results from both the basic and enhanced models.