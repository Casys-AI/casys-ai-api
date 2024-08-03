```mermaid
%% SysML Use Case Diagram for Crushing Mill

%% Define actors
actor "Operator" as Operator
actor "Maintenance Technician" as MaintenanceTechnician

%% Define use cases
usecase UC1 as "UC1: Transform Coffee Beans into Powder"
usecase UC1_1 as "UC1.1: Control Rotary Speed"
usecase UC1_2 as "UC1.2: Apply First-Order Lag"
usecase UC1_3 as "UC1.3: Reduce Speed with Gear"
usecase UC1_4 as "UC1.4: Apply Rotational Spring/Damper"
usecase UC1_5 as "UC1.5: Apply Friction Elements"
usecase UC1_6 as "UC1.6: Monitor Energy Consumption"
usecase UC1_7 as "UC1.7: Enhance Model with Electrical Motor"
usecase UC1_8 as "UC1.8: Control Motor Speed"
usecase UC1_9 as "UC1.9: Monitor Motor Temperature"

%% Define relationships
Operator --> UC1
MaintenanceTechnician --> UC1_6
MaintenanceTechnician --> UC1_9

UC1 --> UC1_1
UC1 --> UC1_2
UC1 --> UC1_3
UC1 --> UC1_4
UC1 --> UC1_5
UC1 --> UC1_6
UC1 --> UC1_7
UC1_7 --> UC1_8
UC1_7 --> UC1_9

%% Add descriptions
UC1: <b>Transform Coffee Beans into Powder</b><br>Transform coffee beans into powder using a crushing mill.
UC1_1: <b>Control Rotary Speed</b><br>Maintain a constant rotary speed for the crushing mill.
UC1_2: <b>Apply First-Order Lag</b><br>Apply a first-order lag to prevent torque peaks.
UC1_3: <b>Reduce Speed with Gear</b><br>Use a speed-reducing gear to adjust the speed.
UC1_4: <b>Apply Rotational Spring/Damper</b><br>Use a rotational spring/damper to manage rotational dynamics.
UC1_5: <b>Apply Friction Elements</b><br>Incorporate friction elements to simulate realistic conditions.
UC1_6: <b>Monitor Energy Consumption</b><br>Use an energy sensor to monitor the energy consumption of the mill.
UC1_7: <b>Enhance Model with Electrical Motor</b><br>Enhance the model by including an electrical motor.
UC1_8: <b>Control Motor Speed</b><br>Control the speed of the electrical motor.
UC1_9: <b>Monitor Motor Temperature</b><br>Monitor the temperature of the electrical motor to account for heat generation.
```