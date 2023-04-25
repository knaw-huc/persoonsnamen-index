based on raa and our model

for this mapping
1. create a database:
  - name = "RAA"

for each row:
1. create a person
  - name = geslachtsnaam
  - givenname = voornaam
  - life_hint_begin = geboortedatum
  - life_hint_end = overlijdensdatum
2. create a record
  - id = id
  - link dat record aan de RAA database
3. create a link
  - href = https://switch.sd.di.huc.knaw.nl/raa/persoon/{id} 