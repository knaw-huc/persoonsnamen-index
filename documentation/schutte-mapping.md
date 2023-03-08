based on schutte_buitenland_met_lemma.xlsx and our model

for this mapping
1. create a database:
- name = "Schutte"

for each row:
1. create a person
  - name = name
  - givenname = givenname
  - life_hint_begin = schutte_beginjaar
  - life_hint_end = schutte_eindjaar
2. create a record
  - id = schutte_nr
3. create a link
  - href = url 