-- Role: republic
-- DROP ROLE IF EXISTS republic;

CREATE ROLE republic WITH
  NOLOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  ENCRYPTED PASSWORD 'md5b8c879892370a0a5bc8c4296dcb76e77';

ALTER ROLE "republic" WITH LOGIN;

GRANT ALL ON SEQUENCE public.database__id_seq TO republic;

GRANT ALL ON SEQUENCE public.links__id_seq TO republic;

GRANT ALL ON SEQUENCE public.persons__id_seq TO republic;

GRANT ALL ON SEQUENCE public.records__id_seq TO republic;

GRANT ALL ON TABLE public.database TO republic;

GRANT ALL ON TABLE public.links TO republic;

GRANT ALL ON TABLE public.persons TO republic;

GRANT ALL ON TABLE public.record_links TO republic;

GRANT ALL ON TABLE public.records TO republic;

