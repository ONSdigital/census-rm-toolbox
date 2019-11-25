begin transaction;
    IF EXISTS(
        SELECT schema_name
          FROM information_schema.schemata
          WHERE schema_name = 'casev2'
      )
    THEN
        drop schema casev2 cascade;
    END IF;

    IF EXISTS(
        SELECT schema_name
          FROM information_schema.schemata
          WHERE schema_name = 'actionv2'
      )
    THEN
        drop schema actionv2 cascade;
    END IF;

    IF EXISTS(
        SELECT schema_name
          FROM information_schema.schemata
          WHERE schema_name = 'uacqid'
      )
    THEN
        drop schema uacqid cascade;
    END IF;
commit transaction;