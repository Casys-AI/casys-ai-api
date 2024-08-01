```mermaid
%% SysML Use Case Diagram for Coffee Machine Digital Twin in Simcenter Amesim

%% Define actors
actor "System Engineer" as SE
actor "Control Engineer" as CE

%% Define use cases
usecase UC1 as "Define Product Architecture"
usecase UC2 as "Size Components"
usecase UC3 as "Develop Physical Plant Models"
usecase UC4 as "Build Component Models"
usecase UC5 as "Verify Component Models"
usecase UC6 as "Assemble Coffee Machine"
usecase UC7 as "Add Control Module"
usecase UC8 as "Incorporate Interactive Elements"
usecase UC9 as "Program Control Logic"

%% Define hierarchical structure
usecase UC4_1 as "Model Reservoirs"
usecase UC4_2 as "Model Crushing Mill"
usecase UC4_3 as "Model Brewer"
usecase UC4_4 as "Model Milk Frother"
usecase UC4_5 as "Model Sugar Dispenser"
usecase UC4_6 as "Model Heater"
usecase UC4_7 as "Model Control Device"

%% Containment relationships
UC4 --> UC4_1
UC4 --> UC4_2
UC4 --> UC4_3
UC4 --> UC4_4
UC4 --> UC4_5
UC4 --> UC4_6
UC4 --> UC4_7

%% Define relationships between actors and use cases
SE --> UC1
SE --> UC2
SE --> UC3
SE --> UC4
SE --> UC5
SE --> UC6
CE --> UC7
CE --> UC8
CE --> UC9

%% Add descriptions
UC1 : ID: UC1\nDescription: Define the overall architecture of the coffee machine.
UC2 : ID: UC2\nDescription: Determine the appropriate sizes for each component.
UC3 : ID: UC3\nDescription: Develop physical models for control development.
UC4 : ID: UC4\nDescription: Create intermediate-detail models for each component.
UC5 : ID: UC5\nDescription: Verify the operation of each component model.
UC6 : ID: UC6\nDescription: Assemble the complete coffee machine model.
UC7 : ID: UC7\nDescription: Add a control module to the coffee machine.
UC8 : ID: UC8\nDescription: Incorporate interactive elements into the model.
UC9 : ID: UC9\nDescription: Use a state chart to program the control logic.
UC4_1 : ID: UC4_1\nDescription: Model the reservoirs of the coffee machine.
UC4_2 : ID: UC4_2\nDescription: Model the crushing mill of the coffee machine.
UC4_3 : ID: UC4_3\nDescription: Model the brewer of the coffee machine.
UC4_4 : ID: UC4_4\nDescription: Model the milk frother of the coffee machine.
UC4_5 : ID: UC4_5\nDescription: Model the sugar dispenser of the coffee machine.
UC4_6 : ID: UC4_6\nDescription: Model the heater of the coffee machine.
UC4_7 : ID: UC4_7\nDescription: Model the control device of the coffee machine.
```