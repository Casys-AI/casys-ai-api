

# sort le graph complet d'un projet
MATCH (p:Project {name: 'crushing_mill'})-[:HAS_DIAGRAM]->(d:Diagram)-[:CONTAINS_ENTITY]->(e:Entity)
RETURN p,d,e

