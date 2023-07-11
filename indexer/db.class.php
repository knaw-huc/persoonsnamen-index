<?php

class db
{
    var $con;

    function __construct()
    {
        $this->con = pg_connect("host=localhost port=5432 dbname=pnindex user=republic password=swellendam");
    }

    function get_items($count)
    {
        $result = pg_query($this->con, "SELECT _id AS id, name, infix, givenname, life_hint_begin, life_hint_end  FROM persons LIMIT $count");
        return $this->ass_arr($result);
    }

    

    function get_database($id) {
        $result = pg_query($this->con, "SELECT \"database\".name FROM records JOIN \"database\" ON \"database\"._id = records.database_id WHERE records.person_id = $id");
        return $this->ass_arr($result);
    }

    private
    function ass_arr($results)
    {
        $retArray = array();
        while ($row = pg_fetch_assoc($results)) {
            $retArray[] = $row;
        }
        return $retArray;
    }
}
